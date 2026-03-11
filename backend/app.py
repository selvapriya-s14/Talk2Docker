from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pathlib import Path
import sys

# Add talk2docker modules to path
base_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(base_dir))

from agent.agent_loop import run_agent_turn
from rag.retriever import Retriever
from llm.cache import response_cache
from llm.request_logger import logger

app = Flask(__name__, template_folder="templates")
CORS(app)

# Lazy-load RAG system (only when first request arrives)
retriever = None

def get_retriever():
    """Lazy-load retriever on first use to speed up app startup"""
    global retriever
    if retriever is None:
        try:
            print("⏳ Loading RAG system (first request)...")
            retriever = Retriever(base_dir / "rag" / "docker_docs", base_dir / "memory")
            print("✅ RAG system loaded!")
        except Exception as e:
            print(f"Warning: Could not initialize RAG retriever: {e}")
            retriever = False  # Use False to mark failed init
    return retriever if retriever is not False else None



# -----------------------------
# Serve frontend UI
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------
# Chat API endpoint (Agent-based)
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    mode = request.json.get("mode", "docker_engine")
    if not user_input:
        return jsonify({"status": "error", "message": "Empty message"})

    # Lazy-load retriever on first request
    current_retriever = get_retriever()
    if not current_retriever and mode == "rag":
        return jsonify({"status": "error", "message": "RAG system not available"})

    try:
        result = run_agent_turn(user_input, current_retriever, mode_override=mode)
        
        response = {
            "status": "success",
            "mode": result.get("mode"),
            "response": result.get("display"),
            "stages": result.get("stages", []),
            "plan": result.get("plan", {}),
        }
        
        # Add tool-specific data
        if result.get("mode") == "tool":
            response["tool"] = result.get("plan", {}).get("tool")
            response["result"] = result.get("result", {})
        
        # Add knowledge-specific data
        if result.get("mode") == "knowledge":
            response["context"] = result.get("context", [])

        # Add dockerfile-specific data
        if result.get("mode") == "dockerfile":
            response["dockerfile_mode"] = result.get("dockerfile_mode")
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# -----------------------------
# Cache stats endpoint
# -----------------------------
@app.route("/api/cache-stats", methods=["GET"])
def cache_stats():
    """Get cache performance statistics"""
    return jsonify(response_cache.stats())


# -----------------------------
# Clear cache endpoint
# -----------------------------
@app.route("/api/cache-clear", methods=["POST"])
def cache_clear():
    """Clear the response cache"""
    response_cache.clear()
    return jsonify({"status": "success", "message": "Cache cleared"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # debug=False for production speed
