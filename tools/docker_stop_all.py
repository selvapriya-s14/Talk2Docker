import subprocess
from typing import Dict


def docker_stop_all() -> Dict[str, str]:
    """Stop all running containers via WSL Docker CLI."""
    try:
        # Get running container IDs
        list_cmd = ["wsl", "docker", "ps", "-q"]
        result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            error = result.stderr.strip()
            if "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Failed to list containers: {error}"}
        
        ids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        
        if not ids:
            return {"status": "success", "output": "No running containers to stop"}
        
        # Stop all containers
        stop_cmd = ["wsl", "docker", "stop"] + ids
        stopped = subprocess.run(stop_cmd, capture_output=True, text=True, timeout=60)
        
        if stopped.returncode == 0:
            count = len(ids)
            return {"status": "success", "output": f"✅ Stopped {count} container{'s' if count > 1 else ''}"}
        else:
            return {"status": "error", "output": f"Failed to stop some containers: {stopped.stderr.strip()}"}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Stop command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
