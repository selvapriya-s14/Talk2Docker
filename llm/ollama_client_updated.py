import json
from typing import Optional
import requests

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral:7b"  # Much faster than deepseek-coder

# Longer timeout for Ollama (120s = 2 minutes for complex prompts)
OLLAMA_TIMEOUT = 120


def generate(prompt: str, model: Optional[str] = None, ollama_url: Optional[str] = None) -> str:
    """Call Ollama and return the raw response text."""
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # More focused responses
            "num_predict": 150,  # Limit response length
        }
    }
    try:
        response = requests.post(ollama_url or DEFAULT_OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except requests.Timeout:
        raise TimeoutError(
            f"⏱️ Ollama timed out after {OLLAMA_TIMEOUT}s. "
            "The LLM is slow or busy. Check if 'ollama serve' is running and not overloaded.\n"
            "Run: ollama serve"
        )
    except requests.ConnectionError:
        raise ConnectionError(
            "❌ Cannot connect to Ollama on localhost:11434.\n"
            "Make sure Ollama is running with: ollama serve"
        )


def generate_json(prompt: str, model: Optional[str] = None, ollama_url: Optional[str] = None) -> dict:
    """Generate a JSON object. Falls back to empty dict on parse failure."""
    try:
        text = generate(prompt, model=model, ollama_url=ollama_url)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end <= start:
            return {}
        return json.loads(text[start:end])
    except (TimeoutError, ConnectionError, json.JSONDecodeError) as e:
        print(f"Warning: Ollama generation failed: {e}")
        return {}
