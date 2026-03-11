from typing import Dict
from tools.registry import TOOLS
from utils.guardrails import validate_tool_call
from utils.docker_check import check_docker_available


# Destructive operations that need warnings
DESTRUCTIVE_TOOLS = {
    "docker_stop_all": "⚠️ This will stop ALL running containers",
    "docker_rm": "⚠️ This will permanently remove the container",
    "docker_rmi": "⚠️ This will permanently remove the image",
    "docker_prune": "⚠️ This will permanently delete unused resources",
}


def execute_tool(tool: str, args: Dict) -> Dict:
    """Execute a tool safely with Docker availability check."""
    # Check if Docker is available
    docker_available, docker_msg = check_docker_available()
    if not docker_available:
        return {
            "status": "error", 
            "output": f"❌ {docker_msg}",
            "error_type": "docker_unavailable"
        }
    
    # Validate tool call
    ok, message = validate_tool_call(tool, args)
    if not ok:
        return {"status": "error", "output": f"❌ {message}"}

    # Get tool function
    fn = TOOLS.get(tool)
    if not fn:
        return {"status": "error", "output": f"❌ Tool '{tool}' not found."}

    # Check if destructive operation
    warning = DESTRUCTIVE_TOOLS.get(tool)
    
    try:
        result = fn(**args)
        # Add warning to destructive operations
        if warning and isinstance(result, dict):
            result["warning"] = warning
        return result
    except TypeError as e:
        return {"status": "error", "output": f"❌ Invalid arguments: {str(e)}"}
    except Exception as e:
        return {"status": "error", "output": f"❌ Execution failed: {str(e)}"}
