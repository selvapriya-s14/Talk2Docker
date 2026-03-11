from typing import Dict
import subprocess


def docker_ps() -> Dict[str, str]:
    """List running containers via WSL Docker CLI."""
    cmd = ["wsl", "docker", "ps", "--format", "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output or "CONTAINER ID" not in output:
                return {"status": "success", "output": "No running containers", "formatted": True}
            return {"status": "success", "output": output, "formatted": True}
        else:
            error = result.stderr.strip()
            if "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Failed to list containers: {error}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
