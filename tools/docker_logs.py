from typing import Dict, Optional
import subprocess


def docker_logs(container: str, tail: Optional[int] = 100, follow: Optional[bool] = False) -> Dict[str, str]:
    """Fetch logs via WSL Docker CLI.

    Args:
        container: container id or name
        tail: number of lines from the end to show
        follow: if True, follow logs (will not return until stopped)
    """
    cmd = ["wsl", "docker", "logs"]
    if tail is not None:
        cmd += ["--tail", str(tail)]
    if follow:
        cmd += ["-f"]
    cmd.append(container)
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
