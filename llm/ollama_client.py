import json
from typing import Optional
import requests
import time

from llm.cache import response_cache
from llm.request_logger import log_request, log_response, log_error

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral:7b"  # Much faster than deepseek-coder


# Timeout for Ollama requests - increased for slower hardware
OLLAMA_TIMEOUT = 300  # 5 minutes to handle slow CPU generation


def validate_input(prompt: str) -> tuple:
    """
    Validate input quality. Return (is_valid, warning_message).
    """
    if len(prompt.strip()) < 10:
        return False, "⚠️ Input too short. Be more specific (e.g., 'MySQL database with Python Flask')"
    
    if len(prompt.strip()) > 8000:
        return False, "⚠️ Input too long. Keep to under 8000 characters"
    
    return True, ""


def generate(prompt: str, model: Optional[str] = None, ollama_url: Optional[str] = None) -> str:
    """Call Ollama and return the raw response text, with caching and retry logic."""
    
    # Quick validation
    is_valid, warning = validate_input(prompt)
    if not is_valid:
        raise ValueError(warning)
    
    # Check cache first
    cached = response_cache.get(prompt)
    if cached:
        stats = response_cache.stats()
        print(f"✅ Cache HIT! {stats['hit_rate']} hit rate. Response from cache.")
        log_response("llm", 0.0, cache_hit=True)
        return cached
    
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # More focused responses
            "num_predict": 500,  # Increased for complete Dockerfile generation
        }
    }
    
    # Retry logic with exponential backoff
    max_retries = 2
    base_delay = 2
    
    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            response = requests.post(ollama_url or DEFAULT_OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            result = data.get("response", "").strip()
            
            # Cache successful response
            response_cache.set(prompt, result)
            
            response_time = time.time() - start_time
            log_response("llm", response_time, cache_hit=False)
            return result
            
        except requests.Timeout:
            error_msg = f"⏱️ Ollama timed out after {OLLAMA_TIMEOUT}s on attempt {attempt + 1}/{max_retries + 1}."
            
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)  # Exponential backoff: 2s, 4s
                print(f"{error_msg} Retrying in {delay}s...")
                log_error("llm", f"Timeout (attempt {attempt + 1}), retrying...")
                time.sleep(delay)
            else:
                error_msg += "\nMistral 7B is very slow on CPU. Consider:\n• Waiting and retrying\n• Using a faster model\n• Adding GPU support"
                log_error("llm", f"Timeout after {max_retries + 1} attempts")
                raise TimeoutError(error_msg)
                
        except requests.ConnectionError:
            log_error("llm", "Connection refused")
            raise ConnectionError(
                "❌ Cannot connect to Ollama on localhost:11434.\n"
                "Make sure Ollama is running with: ollama serve"
            )
    
    raise TimeoutError("Failed to get response after retries")


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
