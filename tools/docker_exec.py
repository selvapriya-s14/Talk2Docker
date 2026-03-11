"""
Execute command in a running Docker container
"""
import subprocess


def docker_exec(container_id: str, command: str):
    """
    Execute a command inside a running Docker container
    
    Args:
        container_id: Container ID or name
        command: Command to execute (e.g., "ls -la", "cat /app/config.txt")
        
    Returns:
        str: Command output or error message
    """
    if not container_id or not isinstance(container_id, str):
        return "Error: container_id is required"
    
    if not command or not isinstance(command, str):
        return "Error: command is required"
    
    try:
        # Split command into parts for proper execution
        cmd_parts = command.split()
        result = subprocess.run(
            ["wsl", "docker", "exec", container_id] + cmd_parts,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip() if result.stdout.strip() else "Command executed successfully (no output)"
        else:
            return f"Error executing command: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
