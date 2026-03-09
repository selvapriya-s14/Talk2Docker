import json

ALLOWED_ACTIONS = [
    "run",
    "stop",
    "restart",
    "remove_container",
    "list_containers",
    "inspect_container",
    "logs",
    "exec",
    "pause",
    "unpause",
    "list_images",
    "pull_image",
    "remove_image",
    "inspect_image",
    "tag_image",
    "system_info",
    "system_df",
    "prune_containers",
    "prune_images",
    "list_networks",
    "list_volumes"
]

def validate(data):

    action = data.get("action")

    if action not in ALLOWED_ACTIONS:
        return False

    return True
