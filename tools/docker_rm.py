"""
Remove Docker container(s)
"""
import subprocess


def docker_rm(container_id: str):
    """
    Remove a Docker container
    
    Args:
        container_id: Container ID or name to remove
        
    Returns:
        str: Success or error message
    """
    if not container_id or not isinstance(container_id, str):
        return {"status": "error", "output": "container_id is required"}
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "rm", container_id],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {"status": "success", "output": f"✅ Container {container_id} removed successfully"}
        else:
            return {"status": "error", "output": f"Error removing container: {result.stderr.strip()}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
