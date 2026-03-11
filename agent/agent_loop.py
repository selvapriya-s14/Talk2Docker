from typing import Dict, Generator, Optional
from agent.planner import plan_action, answer_with_context
from agent.executor import execute_tool
from agent.dockerfile import handle_dockerfile_request
from rag.retriever import Retriever
from llm.request_logger import log_request


def run_agent_turn(user_input: str, retriever: Retriever, mode_override: Optional[str] = None) -> Dict:
    """Single agent step. Returns display data for CLI or UI."""
    if mode_override == "dockerfile":
        log_request("dockerfile", user_input)
        return handle_dockerfile_request(user_input)

    if mode_override == "rag":
        log_request("rag", user_input)
        try:
            context = retriever.retrieve(user_input, top_k=3)
        except Exception:
            context = []

        answer = answer_with_context(user_input, context) if context else f"I don't have information about: {user_input}"
        return {
            "mode": "knowledge",
            "plan": {"mode": "knowledge"},
            "context": context,
            "answer": answer,
            "display": answer,
        }

    log_request("docker_engine", user_input)
    plan = plan_action(user_input)

    if mode_override == "docker_engine" and plan.get("mode") != "tool":
        return {
            "mode": "tool",
            "plan": plan,
            "display": "Docker Engine mode expects a command. Try: 'list containers' or 'run nginx on port 8080'.",
        }

    if plan.get("mode") == "tool":
        # Execute tool directly - no RAG needed
        tool = plan.get("tool", "")
        args = plan.get("args", {})
        result = execute_tool(tool, args)
        
        # Format display message
        output = result.get('output', 'Done')
        warning = result.get('warning', '')
        if warning:
            display = f"{warning}\\n\\n{output}"
        else:
            display = output if not output.startswith('✅') else output
            
        return {
            "mode": "tool", 
            "plan": plan, 
            "result": result, 
            "display": display,
            "stages": [
                {"name": "planning", "status": "complete", "message": "Analyzed query"},
                {"name": "execution", "status": "complete", "message": f"Executed {tool}"},
            ]
        }

    if plan.get("mode") == "chat":
        # Simple chat response - no tools or RAG
        message = plan.get("message", "Hello! How can I help with Docker?")
        return {
            "mode": "chat", 
            "plan": plan, 
            "display": message,
            "stages": [
                {"name": "planning", "status": "complete", "message": "Recognized casual conversation"},
            ]
        }

    # Knowledge mode - retrieve context
    try:
        context = retriever.retrieve(user_input, top_k=3)  # Reduced from 4 to 3 for speed
    except:
        context = []
    
    answer = answer_with_context(user_input, context) if context else f"I don't have information about: {user_input}"
    display = answer
    return {
        "mode": "knowledge", 
        "plan": plan, 
        "context": context, 
        "answer": answer, 
        "display": display,
        "stages": [
            {"name": "planning", "status": "complete", "message": "Identified knowledge query"},
            {"name": "retrieval", "status": "complete", "message": f"Retrieved {len(context)} relevant docs"},
            {"name": "generation", "status": "complete", "message": "Generated answer"},
        ]
    }
