from typing import Dict
import subprocess


def docker_stop(container: str) -> Dict[str, str]:
    """Stop a container via WSL Docker CLI."""
    cmd = ["wsl", "docker", "stop", container]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"status": "success", "output": f"✅ Stopped container {container}"}
        else:
            error = result.stderr.strip()
            if "No such container" in error:
                return {"status": "error", "output": f"Container '{container}' not found"}
            elif "is not running" in error:
                return {"status": "success", "output": f"Container {container} is already stopped"}
            elif "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Failed to stop container: {error}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": f"Stop command timed out for {container}"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
