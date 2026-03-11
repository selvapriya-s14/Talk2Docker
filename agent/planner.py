import json
from typing import Dict, List
from llm.ollama_client import generate_json, generate
from prompts.agent_prompt import SYSTEM_PROMPT


def plan_action(user_input: str) -> Dict:
    """Ask the LLM for a tool or knowledge decision."""
    prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nJSON:"
    data = generate_json(prompt)
    
    # Validate the response has required fields
    if not data or data.get("mode") not in {"tool", "knowledge", "chat"}:
        # Try again with clearer prompt if first attempt failed
        print(f"⚠️ LLM response validation failed. Retrying with fallback prompt.")
        fallback_prompt = (
            f"Extract the Docker command from this request.\n"
            f"Request: {user_input}\n"
            f"Respond with ONLY a JSON object:\n"
            f"Rules:\n"
            f"- 'list' or 'show' containers → {{'mode':'tool','tool':'docker_ps','args':{{}}}}\n"
            f"- 'run' an image → {{'mode':'tool','tool':'docker_run','args':{{'image':'<IMAGE>','port':<PORT>}}}}\n"
            f"- 'show' or 'list' images → {{'mode':'tool','tool':'docker_images','args':{{}}}}\n"
            f"- Otherwise → {{'mode':'knowledge','question':'{user_input}'}}\n"
            f"JSON:"
        )
        data = generate_json(fallback_prompt)
    
    # Final validation - ensure valid mode
    if not data or data.get("mode") not in {"tool", "knowledge", "chat"}:
        return {"mode": "knowledge", "question": user_input}
    
    return data


def answer_with_context(user_input: str, context_chunks: List[str]) -> str:
    """Generate an answer grounded in retrieved context."""
    if not context_chunks:
        return "I don't have documentation on that topic."
    
    context_text = "\n".join(context_chunks[:2])[:1000]  # Limit context length
    prompt = (
        f"Answer in 2-3 sentences max.\n"
        f"Context: {context_text}\n"
        f"Q: {user_input}\nA:"
    )
    answer = generate(prompt).strip()
    # Truncate if too long
    sentences = answer.split('.')[:3]
    return '.'.join(sentences) + '.' if sentences else answer[:200]
