from typing import Dict
import subprocess


def docker_logs(container: str) -> Dict[str, str]:
    """Fetch logs via WSL Docker CLI."""
    cmd = ["wsl", "docker", "logs", "--tail", "100", container]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return {"status": "success", "output": f"No logs for container {container}", "formatted": True}
            # Limit output length
            if len(output) > 5000:
                output = output[-5000:] + "\n... (showing last 5000 characters)"
            return {"status": "success", "output": f"Logs for {container}:\n\n{output}", "formatted": True}
        else:
            error = result.stderr.strip()
            if "No such container" in error:
                return {"status": "error", "output": f"Container '{container}' not found"}
            elif "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Failed to fetch logs: {error}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Log fetch timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
