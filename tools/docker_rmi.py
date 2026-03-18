"""
Remove Docker image(s)
"""
import subprocess


def docker_rmi(image_name: str):
    """
    Remove a Docker image
    
    Args:
        image_name: Image name or ID to remove
        
    Returns:
        str: Success or error message
    """
    if not image_name or not isinstance(image_name, str):
        return {"status": "error", "output": "image_name is required"}
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "rmi", image_name],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            return {"status": "success", "output": f"✅ Image {image_name} removed successfully"}
        else:
            return {"status": "error", "output": f"Error removing image: {result.stderr.strip()}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
