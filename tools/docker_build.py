from typing import Dict, Optional
import subprocess


def docker_build(path: str, tag: Optional[str] = None, dockerfile: Optional[str] = None) -> Dict[str, str]:
    """Build a Docker image via WSL Docker CLI.

    Args:
        path: build context directory (e.g. '.')
        tag: optional image tag (e.g. 'myapp:latest')
        dockerfile: optional Dockerfile name (e.g. 'python.dockerfile')
    """
    cmd = ["wsl", "docker", "build"]
    if tag:
        cmd += ["-t", tag]
    if dockerfile:
        cmd += ["-f", dockerfile]
    cmd.append(path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            out = result.stdout.strip()
            msg = f"✅ Image built successfully"
            if tag:
                msg += f" → tagged as '{tag}'"
            return {"status": "success", "output": msg, "build_log": out}
        else:
            return {"status": "error", "output": f"Build failed:\n{result.stderr.strip()}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Build timed out (5 min limit)"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
