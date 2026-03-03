import docker

client = docker.from_env()

def execute_docker_action(data):

    action = data.get("action")

    # ----------------------------
    # RUN IMAGE
    # ----------------------------
    if action == "run":

        image_name = data.get("image")

        try:
            # Check if image exists locally
            try:
                client.images.get(image_name)
                image_status = "Image already exists locally."
            except:
                # Pull image
                client.images.pull(image_name)
                image_status = "Image pulled successfully."

            # Run container
            container = client.containers.run(
                image_name,
                detach=True,
                ports={"80/tcp": None}  # Random free port
            )

            container.reload()
            ports = container.attrs['NetworkSettings']['Ports']

            return {
                "status": "success",
                "message": image_status,
                "container_id": container.id,
                "ports": ports
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ----------------------------
    # LIST CONTAINERS
    # ----------------------------
    elif action == "list_containers":

        containers = client.containers.list()

        result = []
        for c in containers:
            result.append({
                "id": c.id[:12],
                "name": c.name,
                "image": c.image.tags
            })

        return {"status": "success", "containers": result}

    # ----------------------------
    # LIST IMAGES
    # ----------------------------
    elif action == "list_images":

        images = client.images.list()

        result = []
        for img in images:
            result.append(img.tags)

        return {"status": "success", "images": result}

    # ----------------------------
    # LOGS
    # ----------------------------
    elif action == "logs":

        name = data.get("name")

        try:
            container = client.containers.get(name)
            logs = container.logs().decode("utf-8")

            return {
                "status": "success",
                "logs": logs
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    else:
        return {"status": "error", "message": "Invalid action"}
