"""
Docker availability checker
"""
import subprocess
from typing import Tuple


_docker_status_cache = {"available": None, "message": ""}


def check_docker_available(use_cache: bool = True) -> Tuple[bool, str]:
    """
    Check if Docker is available and running
    
    Args:
        use_cache: Use cached result if available (default: True)
        
    Returns:
        Tuple of (is_available, message)
    """
    if use_cache and _docker_status_cache["available"] is not None:
        return _docker_status_cache["available"], _docker_status_cache["message"]
    
    try:
        result = subprocess.run(
            ["wsl", "docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            _docker_status_cache["available"] = True
            _docker_status_cache["message"] = f"Docker {version}"
            return True, f"Docker {version}"
        else:
            error_msg = result.stderr.strip()
            if "Cannot connect" in error_msg or "connection refused" in error_msg.lower():
                msg = "Docker daemon is not running. Start it with: wsl sudo systemctl start docker"
            else:
                msg = f"Docker not available: {error_msg}"
            
            _docker_status_cache["available"] = False
            _docker_status_cache["message"] = msg
            return False, msg
            
    except subprocess.TimeoutExpired:
        msg = "⏱️ Docker check timed out (15s). WSL may be slow. Try again in a moment."
        _docker_status_cache["available"] = False
        _docker_status_cache["message"] = msg
        return False, msg
        
    except FileNotFoundError:
        msg = "WSL not installed or 'docker' command not found. Install Docker on WSL."
        _docker_status_cache["available"] = False
        _docker_status_cache["message"] = msg
        return False, msg
        
    except Exception as e:
        msg = f"Docker check failed: {str(e)}"
        _docker_status_cache["available"] = False
        _docker_status_cache["message"] = msg
        return False, msg
