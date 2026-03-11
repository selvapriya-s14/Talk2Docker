from typing import Dict, Optional
import subprocess
import time
from tools.docker_utils import wait_and_check_container


def docker_run(image: str, port: Optional[int] = None) -> Dict[str, str]:
    """Run a container using WSL Docker CLI."""
    cmd = ["wsl", "docker", "run", "-d"]
    if port is not None:
        cmd += ["-p", f"{port}:80"]
    cmd.append(image)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            container_id = result.stdout.strip()[:12]  # Short ID
            
            # Check if container crashes immediately
            check_result = wait_and_check_container(container_id, wait_seconds=2)
            
            if check_result["success"]:
                msg = f"✅ Started container {container_id} from {image}"
                if port:
                    msg += f" → http://localhost:{port}"
                return {"status": "success", "output": msg, "container_id": container_id}
            else:
                # Container crashed - show logs
                logs = check_result.get("logs", "")
                error_msg = f"❌ Container {container_id} crashed immediately\n\n📋 Error Logs:\n{logs}"
                return {"status": "error", "output": error_msg, "container_id": container_id, "formatted": True}
        else:
            error = result.stderr.strip()
            if "Unable to find image" in error:
                return {"status": "error", "output": f"Image '{image}' not found. Try: docker pull {image}"}
            elif "port is already allocated" in error:
                return {"status": "error", "output": f"Port {port} is already in use. Choose a different port."}
            elif "Cannot connect" in error:
                return {"status": "error", "output": "Docker daemon not running"}
            return {"status": "error", "output": f"Failed to start container: {error}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Container start timed out"}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}
