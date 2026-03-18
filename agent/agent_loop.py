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
        result = handle_dockerfile_request(user_input)
        # Append compose + env to display when available
        display = result.get("display", "")
        if result.get("compose"):
            display += f"\n\n{'='*60}\n📦 docker-compose.yml\n{'='*60}\n{result['compose']}"
        if result.get("env"):
            display += f"\n\n{'='*60}\n📝 .env.example\n{'='*60}\n{result['env']}"
        result["display"] = display
        return result

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

        # Special formatting for docker_ports
        if tool == "docker_ports" and result.get("status") == "success":
            ports = result.get("ports", [])
            summary = result.get("summary")
            if summary:
                output = f"🔌 Published ports: {summary}\n"
            else:
                output = "🔌 No published ports found.\n"
            for p in ports:
                cp = p.get("container_port", "?")
                bindings = p.get("bindings", [])
                if bindings:
                    for b in bindings:
                        output += f"  {cp} → {b.get('HostIp','0.0.0.0')}:{b.get('HostPort','?')}\n"
                else:
                    output += f"  {cp} (exposed but not published)\n"

        # Special formatting for docker_inspect
        if tool == "docker_inspect" and result.get("status") == "success" and result.get("inspect"):
            info = result["inspect"][0] if isinstance(result["inspect"], list) else result["inspect"]
            name = info.get("Name", "?").lstrip("/")
            state = info.get("State", {})
            config = info.get("Config", {})
            net = info.get("NetworkSettings", {})

            lines = [f"🔍 Inspect: {name}"]
            lines.append(f"  Status: {state.get('Status', '?')}")
            lines.append(f"  Image: {config.get('Image', '?')}")
            # Ports
            ports = net.get("Ports", {})
            if ports:
                lines.append("  Ports:")
                for cp, bindings in ports.items():
                    if bindings:
                        for b in bindings:
                            lines.append(f"    {cp} → {b.get('HostIp','0.0.0.0')}:{b.get('HostPort','?')}")
                    else:
                        lines.append(f"    {cp} (not published)")
            # Mounts
            mounts = info.get("Mounts", [])
            if mounts:
                lines.append("  Mounts:")
                for m in mounts:
                    lines.append(f"    {m.get('Source', '?')} → {m.get('Destination', '?')} ({m.get('Type', '?')})")
            # Env (show non-sensitive ones)
            envs = config.get("Env", [])
            if envs:
                lines.append(f"  Env vars: {len(envs)} set")

            output = "\n".join(lines)

        if warning:
            display = f"{warning}\n\n{output}"
        else:
            display = output
            
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
