import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:7b-instruct"

def ask_llm(user_input):

    prompt = f"""
You are Talk2Docker AI Assistant.

Your job is to convert user commands into Docker JSON commands.

IMPORTANT RULES:
- Always return ONLY JSON.
- Never explain commands.
- Never ask the user to choose actions.
- Never output plain text.
RULES:
- If the user says only "list", ask:
  "List what? (images or containers or networks or volumes)"
- If the user asks for images → use action list_images
- If the user asks for containers → use action list_containers
- If the user asks for networks → use action list_networks
- If the user asks for volumes → use action list_volumes
Docker command format:

{{
"type": "docker",
"action": "ACTION_NAME"
}}

Supported actions:

list_images
list_containers
run
stop
restart
remove_container
logs
inspect_container
pull_image
remove_image
inspect_image
system_info
system_df
prune_containers
prune_images
list_networks
list_volumes

Mappings:

User: list images
Return:
{{
"type": "docker",
"action": "list_images"
}}

User: list containers
Return:
{{
"type": "docker",
"action": "list_containers"
}}

User: run nginx
Return:
{{
"type": "docker",
"action": "run",
"image": "nginx"
}}

User: stop nginx
Return:
{{
"type": "docker",
"action": "stop",
"name": "nginx"
}}

User: list
Return:
{{
"type": "chat",
"message": "List what? (images, containers, volumes, networks)"
}}

User message:
{user_input}
"""


    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
        "temperature": 0
        }
    })

    result = response.json()["response"]

    # Extract JSON safely
    start = result.find("{")
    end = result.rfind("}") + 1
    json_text = result[start:end]

    try:
        return json.loads(json_text)
    except:
        return {
            "type": "chat",
            "message": "Sorry, I could not understand that."
        }
