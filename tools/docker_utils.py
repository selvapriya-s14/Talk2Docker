"""
Docker utility functions for enhanced error handling
"""
import subprocess
import time
from typing import Tuple, Dict


def check_container_status(container_id: str) -> Tuple[bool, str]:
    """
    Check if a container is running or has crashed
    
    Args:
        container_id: Container ID or name
        
    Returns:
        Tuple of (is_running, status_message)
    """
    try:
        result = subprocess.run(
            ["wsl", "docker", "inspect", "-f", "{{.State.Running}}", container_id],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            is_running = "true" in result.stdout.lower()
            if is_running:
                return True, "running"
            else:
                # Get exit code
                exit_result = subprocess.run(
                    ["wsl", "docker", "inspect", "-f", "{{.State.ExitCode}}", container_id],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                exit_code = exit_result.stdout.strip()
                return False, f"exited({exit_code})"
        else:
            return False, "unknown"
    except:
        return False, "unknown"


def get_container_logs(container_id: str, tail: int = 50) -> str:
    """
    Fetch container logs
    
    Args:
        container_id: Container ID or name
        tail: Number of lines to fetch from end
        
    Returns:
        Log content
    """
    try:
        result = subprocess.run(
            ["wsl", "docker", "logs", "--tail", str(tail), container_id],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout.strip()
            if result.stderr.strip():
                logs += "\n" + result.stderr.strip()
            return logs if logs else "(no logs available)"
        else:
            return f"(could not fetch logs: {result.stderr.strip()})"
    except:
        return "(could not fetch logs)"


def wait_and_check_container(container_id: str, wait_seconds: int = 2) -> Dict:
    """
    Wait for container to stabilize and check if it crashes
    
    Args:
        container_id: Container ID or name
        wait_seconds: Seconds to wait before checking
        
    Returns:
        Dict with status and logs if crashed
    """
    time.sleep(wait_seconds)
    
    is_running, status = check_container_status(container_id)
    
    if is_running:
        return {
            "success": True,
            "status": "running",
            "logs": None
        }
    else:
        logs = get_container_logs(container_id, tail=100)
        return {
            "success": False,
            "status": status,
            "logs": logs
        }
