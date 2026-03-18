from typing import Any, Dict, Tuple

ALLOWED_TOOLS = {
    "docker_run",
    "docker_ps",
    "docker_logs",
    "docker_stop",
    "docker_stop_all",
    "docker_build",
    "docker_images",
    "docker_rm",
    "docker_rmi",
    "docker_exec",
    "docker_inspect",
    "docker_ports",
    "docker_stats",
    "docker_network",
    "docker_volume",
    "docker_restart",
    "docker_prune",
    "docker_pull",
}


def validate_tool_call(tool: str, args: Dict[str, Any]) -> Tuple[bool, str]:
    if tool not in ALLOWED_TOOLS:
        return False, f"Tool '{tool}' is not allowed."

    if tool == "docker_run":
        image = args.get("image")
        if not image or not isinstance(image, str):
            return False, "docker_run requires a string 'image'."
        port = args.get("port")
        if port is not None and not isinstance(port, int):
            return False, "docker_run 'port' must be an integer."

    if tool in {"docker_logs", "docker_stop"}:
        name = args.get("container")
        if not name or not isinstance(name, str):
            return False, f"{tool} requires a string 'container'."

    if tool == "docker_stop_all":
        if args:
            return False, "docker_stop_all does not take arguments."

    if tool == "docker_build":
        path = args.get("path")
        if not path or not isinstance(path, str):
            return False, "docker_build requires a string 'path'."
        # tag and dockerfile are optional strings
        tag = args.get("tag")
        if tag is not None and not isinstance(tag, str):
            return False, "docker_build 'tag' must be a string."
        dockerfile = args.get("dockerfile")
        if dockerfile is not None and not isinstance(dockerfile, str):
            return False, "docker_build 'dockerfile' must be a string."

    if tool == "docker_images":
        if args:
            return False, "docker_images does not take arguments."

    if tool == "docker_ps":
        if args:
            return False, "docker_ps does not take arguments."

    if tool == "docker_rm":
        container_id = args.get("container_id")
        if not container_id or not isinstance(container_id, str):
            return False, "docker_rm requires a string 'container_id'."

    if tool == "docker_rmi":
        image_name = args.get("image_name")
        if not image_name or not isinstance(image_name, str):
            return False, "docker_rmi requires a string 'image_name'."

    if tool == "docker_exec":
        container_id = args.get("container_id")
        command = args.get("command")
        if not container_id or not isinstance(container_id, str):
            return False, "docker_exec requires a string 'container_id'."
        if not command or not isinstance(command, str):
            return False, "docker_exec requires a string 'command'."

    if tool == "docker_inspect":
        name = args.get("name")
        if not name or not isinstance(name, str):
            return False, "docker_inspect requires a string 'name'."

    if tool == "docker_ports":
        name = args.get("container") or args.get("container_id") or args.get("name")
        if not name or not isinstance(name, str):
            return False, "docker_ports requires a string 'container' or 'container_id'."

    if tool == "docker_restart":
        container_id = args.get("container_id")
        if not container_id or not isinstance(container_id, str):
            return False, "docker_restart requires a string 'container_id'."

    if tool == "docker_prune":
        resource_type = args.get("resource_type", "container")
        if resource_type not in ["container", "image", "volume", "network", "all"]:
            return False, "docker_prune 'resource_type' must be 'container', 'image', 'volume', 'network', or 'all'."

    if tool == "docker_pull":
        image_name = args.get("image_name")
        if not image_name or not isinstance(image_name, str):
            return False, "docker_pull requires a string 'image_name'."

    if tool == "docker_stats":
        pass  # container is optional

    if tool == "docker_network":
        action = args.get("action", "ls")
        if action not in ("ls", "create", "rm", "remove", "inspect"):
            return False, "docker_network 'action' must be 'ls', 'create', 'rm', or 'inspect'."

    if tool == "docker_volume":
        action = args.get("action", "ls")
        if action not in ("ls", "create", "rm", "remove", "inspect"):
            return False, "docker_volume 'action' must be 'ls', 'create', 'rm', or 'inspect'."

    return True, "ok"
