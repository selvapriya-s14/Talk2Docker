def rule_based_parser(text):

    text = text.lower()

    # List images
    if "list images" in text:
        return {"action": "list_images"}

    # List containers
    if "list containers" in text or "running containers" in text:
        return {"action": "list_containers"}

    # Run container
    if "run" in text or "start" in text:
        words = text.split()
        image = words[-1]
        return {"action": "run", "image": image}

    # Logs
    if "logs" in text:
        words = text.split()
        return {"action": "logs", "name": words[-1]}

    # Stop container
    if "stop" in text:
        words = text.split()
        return {"action": "stop", "name": words[-1]}

    return None
