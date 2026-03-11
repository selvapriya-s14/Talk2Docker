"""
List all Docker images
"""
import subprocess
from typing import Dict


def docker_images() -> Dict[str, str]:
    """
    List all Docker images available locally
    
    Returns:
        Dict with status and formatted output
    """
    try:
        result = subprocess.run(
            ["wsl", "docker", "images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output or output == "REPOSITORY":
                return {"status": "success", "output": "No images found", "formatted": True}
            return {"status": "success", "output": output, "formatted": True}
        else:
            error = result.stderr.strip()
            if "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Failed to list images: {error}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
