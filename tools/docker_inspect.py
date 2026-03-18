"""
Inspect Docker container or image
"""
import subprocess
import json


def docker_inspect(name: str):
    """
    Get detailed information about a Docker container or image
    
    Args:
        name: Container or image name/ID
        
    Returns:
        str: Detailed JSON information
    """
    if not name or not isinstance(name, str):
        return {"status": "error", "output": "name is required"}
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "inspect", name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            out = result.stdout.strip()
            try:
                parsed = json.loads(out)
                return {"status": "success", "inspect": parsed}
            except Exception:
                return {"status": "success", "output": out}
        else:
            return {"status": "error", "output": f"Error inspecting: {result.stderr.strip()}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
