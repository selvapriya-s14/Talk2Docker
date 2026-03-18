from typing import Dict, Optional
import subprocess
import time
from tools.docker_utils import wait_and_check_container

# Well-known container ports for popular images
KNOWN_PORTS = {
    "nginx": 80,
    "httpd": 80,
    "apache": 80,
    "tomcat": 8080,
    "node": 3000,
    "express": 3000,
    "react": 3000,
    "nextjs": 3000,
    "flask": 5000,
    "django": 8000,
    "fastapi": 8000,
    "uvicorn": 8000,
    "spring": 8080,
    "redis": 6379,
    "postgres": 5432,
    "postgresql": 5432,
    "mysql": 3306,
    "mongo": 27017,
    "mongodb": 27017,
    "rabbitmq": 5672,
    "elasticsearch": 9200,
    "jenkins": 8080,
    "grafana": 3000,
    "prometheus": 9090,
    "portainer": 9000,
    "traefik": 80,
    "caddy": 80,
    "sonarqube": 9000,
    "gitlab": 80,
    "minio": 9000,
}


def _guess_container_port(image: str) -> int:
    """Guess internal container port from image name."""
    base = image.split(":")[0].split("/")[-1].lower()
    return KNOWN_PORTS.get(base, 80)


def docker_run(image: str, port: Optional[int] = None, container_port: Optional[int] = None) -> Dict[str, str]:
    """Run a container using WSL Docker CLI.

    Args:
        image: Docker image name
        port: host port to expose
        container_port: internal container port (auto-detected if omitted)
    """
    cmd = ["wsl", "docker", "run", "-d"]
    if port is not None:
        internal = container_port or _guess_container_port(image)
        cmd += ["-p", f"{port}:{internal}"]
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
                    internal = container_port or _guess_container_port(image)
                    msg += f" → http://localhost:{port} (host:{port} → container:{internal})"
                return {"status": "success", "output": msg, "container_id": container_id}
            else:
                # Check if it's a one-shot container that exited successfully (exit code 0)
                status = check_result.get("status", "")
                logs = check_result.get("logs", "")
                if "exited(0)" in status:
                    # One-shot container (e.g., hello-world) — ran and finished successfully
                    msg = f"✅ Container {container_id} from {image} ran and completed successfully (one-shot).\n\n📋 Output:\n{logs}"
                    return {"status": "success", "output": msg, "container_id": container_id, "formatted": True}
                else:
                    # Container actually crashed
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
