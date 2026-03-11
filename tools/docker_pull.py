"""
Pull Docker image from registry
"""
import subprocess


def docker_pull(image_name: str):
    """
    Pull a Docker image from Docker Hub or other registry
    
    Args:
        image_name: Image to pull (e.g., "nginx:latest", "python:3.11")
        
    Returns:
        str: Success or error message
    """
    if not image_name or not isinstance(image_name, str):
        return "Error: image_name is required"
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "pull", image_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for large images
        )
        
        if result.returncode == 0:
            return f"Image {image_name} pulled successfully"
        else:
            return f"Error pulling image: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Pull timed out (image may be too large)"
    except Exception as e:
        return f"Error: {str(e)}"
