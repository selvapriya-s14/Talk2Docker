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
        return "Error: image_name is required"
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "rmi", image_name],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            return f"Image {image_name} removed successfully"
        else:
            return f"Error removing image: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
