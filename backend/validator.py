import json

ALLOWED_ACTIONS = [
    "run",
    "list_images",
    "list_containers",
    "logs",
    "stop"
]

def validate(data):

    action = data.get("action")

    if action not in ALLOWED_ACTIONS:
        return False

    return True
