"""Docker client helper that connects to WSL2 Docker daemon."""
import docker
import subprocess
import time
from typing import Optional


def start_docker_in_wsl() -> bool:
    """Start Docker service in WSL2 if not running."""
    try:
        # Check if Docker is already running
        result = subprocess.run(
            ["wsl", "sudo", "systemctl", "is-active", "docker"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "active" in result.stdout:
            return True  # Already running
        
        # Start Docker
        print("Starting Docker in WSL2...")
        subprocess.run(
            ["wsl", "sudo", "systemctl", "start", "docker"],
            capture_output=True,
            timeout=10,
            check=True
        )
        
        # Wait for Docker to be ready (max 10 seconds)
        for _ in range(10):
            time.sleep(1)
            test = subprocess.run(
                ["wsl", "docker", "ps"],
                capture_output=True,
                timeout=3
            )
            if test.returncode == 0:
                print("✅ Docker started successfully in WSL2")
                return True
        
        return False
    except Exception as e:
        print(f"⚠️ Could not auto-start Docker: {e}")
        return False


def get_docker_client() -> docker.DockerClient:
    """Get Docker client, trying WSL2 connection first."""
    # Try different connection methods
    connection_attempts = [
        "tcp://localhost:2375",  # TCP connection (WSL2)
        "unix:///var/run/docker.sock",  # Standard Unix socket (WSL2)
        "npipe:////./pipe/docker_engine",  # Windows Docker Desktop
        None,  # Environment default
    ]
    
    last_error = None
    for base_url in connection_attempts:
        try:
            if base_url:
                client = docker.DockerClient(base_url=base_url)
            else:
                client = docker.from_env()
            
            # Test connection
            client.ping()
            return client
        except Exception as e:
            last_error = e
            continue
    
    # If all connection attempts failed, try to start Docker in WSL2
    if start_docker_in_wsl():
        # Retry TCP connection after starting Docker
        time.sleep(2)
        try:
            client = docker.DockerClient(base_url="tcp://localhost:2375")
            client.ping()
            return client
        except Exception as e:
            last_error = e
    
    # If all fail, raise the last error
    raise Exception(f"⚠️ Cannot connect to Docker. Please start Docker manually.\nError: {last_error}")


# Cached client instance
_client: Optional[docker.DockerClient] = None


def get_client() -> docker.DockerClient:
    """Get or create cached Docker client."""
    global _client
    if _client is None:
        _client = get_docker_client()
    return _client
