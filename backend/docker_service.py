import docker

client = docker.from_env()

def execute_docker_action(data):

    action = data.get("action")

    try:

        # -------------------------
        # LIST IMAGES
        # -------------------------
        if action == "list_images":

            images = client.images.list()

            if not images:
                return {"status": "success", "message": "No Docker images found"}

            result = []
            for img in images:
                result.append(img.tags)

            return {"status": "success", "images": result}

        # -------------------------
        # LIST CONTAINERS
        # -------------------------
        elif action == "list_containers":

            containers = client.containers.list()

            if not containers:
                return {"status": "success", "message": "No running containers"}

            result = []

            for c in containers:
                result.append({
                    "id": c.id[:12],
                    "name": c.name,
                    "image": c.image.tags
                })

            return {"status": "success", "containers": result}

        # -------------------------
        # RUN CONTAINER
        # -------------------------
        elif action == "run":

            image = data.get("image")
            name = data.get("name")

            if not image:
                return {"status": "error", "message": "Image name required"}

            try:
                client.images.get(image)
            except:
                client.images.pull(image)

            container = client.containers.run(
                image,
                name=name,
                detach=True,
                ports={"80/tcp": None}
            )

            return {
                "status": "success",
                "message": f"Container {container.name} started",
                "container_id": container.id[:12]
            }

        # -------------------------
        # STOP CONTAINER
        # -------------------------
        elif action == "stop":

            name = data.get("name")

            container = client.containers.get(name)
            container.stop()

            return {
                "status": "success",
                "message": f"Container {name} stopped"
            }

        # -------------------------
        # RESTART CONTAINER
        # -------------------------
        elif action == "restart":

            name = data.get("name")

            container = client.containers.get(name)
            container.restart()

            return {
                "status": "success",
                "message": f"Container {name} restarted"
            }

        # -------------------------
        # REMOVE CONTAINER
        # -------------------------
        elif action == "remove_container":

            name = data.get("name")

            container = client.containers.get(name)
            container.remove(force=True)

            return {
                "status": "success",
                "message": f"Container {name} removed"
            }

        # -------------------------
        # CONTAINER LOGS
        # -------------------------
        elif action == "logs":

            name = data.get("name")

            container = client.containers.get(name)

            logs = container.logs(tail=50).decode("utf-8")

            return {
                "status": "success",
                "logs": logs
            }

        # -------------------------
        # INSPECT CONTAINER
        # -------------------------
        elif action == "inspect_container":

            name = data.get("name")

            container = client.containers.get(name)

            info = container.attrs

            return {
                "status": "success",
                "message": f"Container {name} inspected",
                "details": info
            }

        # -------------------------
        # PULL IMAGE
        # -------------------------
        elif action == "pull_image":

            image = data.get("image")

            client.images.pull(image)

            return {
                "status": "success",
                "message": f"Image {image} pulled successfully"
            }

        # -------------------------
        # REMOVE IMAGE
        # -------------------------
        elif action == "remove_image":

            image = data.get("image")

            client.images.remove(image)

            return {
                "status": "success",
                "message": f"Image {image} removed"
            }

        # -------------------------
        # INSPECT IMAGE
        # -------------------------
        elif action == "inspect_image":

            image = data.get("image")

            img = client.images.get(image)

            return {
                "status": "success",
                "details": img.attrs
            }

        # -------------------------
        # SYSTEM INFO
        # -------------------------
        elif action == "system_info":

            info = client.info()

            return {
                "status": "success",
                "message": f"Docker running with {info['Containers']} containers and {info['Images']} images"
            }

        # -------------------------
        # SYSTEM DISK USAGE
        # -------------------------
        elif action == "system_df":

            df = client.df()

            return {
                "status": "success",
                "details": df
            }

        # -------------------------
        # PRUNE CONTAINERS
        # -------------------------
        elif action == "prune_containers":

            result = client.containers.prune()

            return {
                "status": "success",
                "message": "Unused containers removed",
                "details": result
            }

        # -------------------------
        # PRUNE IMAGES
        # -------------------------
        elif action == "prune_images":

            result = client.images.prune()

            return {
                "status": "success",
                "message": "Unused images removed",
                "details": result
            }

        # -------------------------
        # LIST NETWORKS
        # -------------------------
        elif action == "list_networks":

            networks = client.networks.list()

            result = [n.name for n in networks]

            return {
                "status": "success",
                "networks": result
            }

        # -------------------------
        # LIST VOLUMES
        # -------------------------
        elif action == "list_volumes":

            volumes = client.volumes.list()

            result = [v.name for v in volumes]

            return {
                "status": "success",
                "volumes": result
            }

        # -------------------------
        # INVALID ACTION
        # -------------------------
        else:

            return {
                "status": "error",
                "message": "Unsupported Docker action"
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
