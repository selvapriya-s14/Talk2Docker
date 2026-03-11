"""
Inspect Docker container or image
"""
import subprocess


def docker_inspect(name: str):
    """
    Get detailed information about a Docker container or image
    
    Args:
        name: Container or image name/ID
        
    Returns:
        str: Detailed JSON information
    """
    if not name or not isinstance(name, str):
        return "Error: name is required"
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "inspect", name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error inspecting: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
