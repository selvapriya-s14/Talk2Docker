from flask import Flask, request, jsonify, render_template
from backend.llm_service import ask_llm
from backend.docker_service import execute_docker_action
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)  # Optional: only if frontend is on different origin

# -----------------------------
# Serve frontend UI
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")  # loads backend/templates/index.html

# -----------------------------
# Chat API endpoint
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    # Call your LLM service
    llm_output = ask_llm(user_input)

    # If AI decides it's just a chat question
    if llm_output["type"] == "chat":
        return jsonify({
            "status": "success",
            "message": llm_output["message"]
        })

    # If AI decides it's a Docker command
    if llm_output["type"] == "docker":
        docker_result = execute_docker_action(llm_output)
        return jsonify(docker_result)

    # Fallback
    return jsonify({
        "status": "error",
        "message": "Invalid response from AI"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
