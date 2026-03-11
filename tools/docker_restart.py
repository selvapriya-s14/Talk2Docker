"""
Restart Docker container
"""
import subprocess
from tools.docker_utils import wait_and_check_container


def docker_restart(container_id: str):
    """
    Restart a running Docker container
    
    Args:
        container_id: Container ID or name to restart
        
    Returns:
        str: Success or error message
    """
    if not container_id or not isinstance(container_id, str):
        return {"status": "error", "output": "Error: container_id is required"}
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "restart", container_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Check if container crashes after restart
            check_result = wait_and_check_container(container_id, wait_seconds=2)
            
            if check_result["success"]:
                return {"status": "success", "output": f"✅ Container {container_id} restarted successfully"}
            else:
                # Container crashed after restart - show logs
                logs = check_result.get("logs", "")
                error_msg = f"⚠️ Container {container_id} restarted but crashed\n\n📋 Error Logs:\n{logs}"
                return {"status": "error", "output": error_msg, "formatted": True}
        else:
            error = result.stderr.strip()
            if "No such container" in error:
                return {"status": "error", "output": f"Container '{container_id}' not found"}
            elif "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Error restarting container: {error}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Error: Command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
