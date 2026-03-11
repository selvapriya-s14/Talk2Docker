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
            timeout=30
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
        # WSL is slow - assume Docker is available and let it try anyway
        msg = "⏱️ Docker check timed out (WSL is slow), but proceeding anyway..."
        _docker_status_cache["available"] = True  # Assume available on timeout
        _docker_status_cache["message"] = msg
        return True, msg
    except Exception as e:
        msg = f"Cannot check Docker: {str(e)}"
        _docker_status_cache["available"] = False
        _docker_status_cache["message"] = msg
        return False, msg


def reset_docker_cache():
    """Reset the Docker availability cache"""
    _docker_status_cache["available"] = None
    _docker_status_cache["message"] = ""
