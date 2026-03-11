from typing import Dict
import subprocess


def docker_build(path: str) -> Dict[str, str]:
    """Build a Docker image via WSL Docker CLI."""
    cmd = ["wsl", "docker", "build", path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": (e.stderr or e.stdout).strip()}
