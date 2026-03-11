"""
Prune/cleanup Docker resources
"""
import subprocess


def docker_prune(resource_type: str = "container"):
    """
    Remove unused Docker resources (containers, images, volumes, networks)
    
    Args:
        resource_type: Type to prune - "container", "image", "volume", "network", or "all"
        
    Returns:
        str: Success message with reclaimed space or error
    """
    if not resource_type or resource_type not in ["container", "image", "volume", "network", "all"]:
        return "Error: resource_type must be 'container', 'image', 'volume', 'network', or 'all'"
    
    try:
        if resource_type == "all":
            cmd = ["wsl", "docker", "system", "prune", "-a", "-f"]
        elif resource_type == "image":
            cmd = ["wsl", "docker", "image", "prune", "-a", "-f"]
        else:
            cmd = ["wsl", "docker", resource_type, "prune", "-f"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else f"Pruned {resource_type}s successfully"
        else:
            return f"Error pruning {resource_type}s: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
