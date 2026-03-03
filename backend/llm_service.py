import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:7b-instruct"

def ask_llm(user_input):

    prompt = f"""
You are Talk2Docker AI Assistant.

You can:
1. Answer general knowledge questions.
2. Have friendly conversation.
3. Control Docker using structured commands.

Supported Docker actions:
- list_images
- list_containers
- run (requires image)
- stop (requires container name)
- logs (requires container name)

If the user message is normal conversation or general question:
Respond in this JSON format:
{{
  "type": "chat",
  "message": "your response"
}}

If the user wants Docker action:
Respond ONLY in this JSON format:
{{
  "type": "docker",
  "action": "run",
  "image": "nginx"
}}

IMPORTANT:
- Always return valid JSON.
- Do not return explanation outside JSON.

User: {user_input}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
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
