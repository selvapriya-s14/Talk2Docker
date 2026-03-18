import json
import re
from typing import Dict, List, Optional
from llm.ollama_client import generate_json, generate
from prompts.agent_prompt import SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Fast deterministic planner — matches common intents WITHOUT calling the LLM.
# This makes ~80% of Docker commands respond in <50ms instead of 5-45s.
# ---------------------------------------------------------------------------

def _extract_entity(text: str, after_keywords: list[str]) -> Optional[str]:
    """Extract the first meaningful token after any of the given keywords."""
    lower = text.lower()
    for kw in after_keywords:
        idx = lower.find(kw)
        if idx != -1:
            rest = text[idx + len(kw):].strip()
            # take first token (container id, name, image)
            token = rest.split()[0] if rest.split() else None
            if token:
                return token.strip("'\"`,.")
    return None


def _extract_port(text: str) -> Optional[int]:
    """Extract port number from text like 'on port 8080' or 'port 3000'."""
    m = re.search(r'(?:port|PORT)\s*(\d{2,5})', text)
    if m:
        return int(m.group(1))
    # also match :8080 pattern
    m = re.search(r':(\d{2,5})', text)
    if m:
        return int(m.group(1))
    return None


def _fast_plan(user_input: str) -> Optional[Dict]:
    """
    Rule-based planner for common Docker commands.
    Returns a plan dict or None if no rule matches.
    """
    text = user_input.strip()
    lower = text.lower()
    words = lower.split()

    # --- Greetings / chat ---
    if lower in ("hi", "hello", "hey", "thanks", "thank you", "bye", "ok"):
        return {"mode": "chat", "message": "Hi! I help with Docker commands. Try 'list containers' or 'run nginx on port 8080'."}

    # --- List / show containers ---
    if re.search(r'\b(list|show|get|display)\b.*\bcontainer', lower):
        return {"mode": "tool", "tool": "docker_ps", "args": {}}

    # --- List / show images ---
    if re.search(r'\b(list|show|get|display)\b.*\bimage', lower):
        return {"mode": "tool", "tool": "docker_images", "args": {}}

    # --- Stop all ---
    if re.search(r'\bstop\s+all\b', lower) or re.search(r'\bkill\s+all\b', lower):
        return {"mode": "tool", "tool": "docker_stop_all", "args": {}}

    # --- Stop container ---
    if re.search(r'\bstop\b', lower):
        entity = _extract_entity(text, ["stop container ", "stop "])
        if entity and entity not in ("container", "containers", "all"):
            return {"mode": "tool", "tool": "docker_stop", "args": {"container": entity}}

    # --- Restart container ---
    if re.search(r'\brestart\b', lower):
        entity = _extract_entity(text, ["restart container ", "restart "])
        if entity and entity not in ("container", "containers"):
            return {"mode": "tool", "tool": "docker_restart", "args": {"container_id": entity}}

    # --- Remove container ---
    if re.search(r'\b(remove|delete|rm)\b.*\bcontainer\b', lower):
        entity = _extract_entity(text, ["container ", "rm "])
        if entity:
            return {"mode": "tool", "tool": "docker_rm", "args": {"container_id": entity}}

    # --- Remove image ---
    if re.search(r'\b(remove|delete|rmi)\b.*\bimage\b', lower):
        entity = _extract_entity(text, ["image ", "rmi "])
        if entity:
            return {"mode": "tool", "tool": "docker_rmi", "args": {"image_name": entity}}

    # --- Logs ---
    if re.search(r'\blog(s)?\b', lower):
        entity = _extract_entity(text, ["logs for ", "logs from ", "logs of ", "logs ", "log for ", "log from ", "log "])
        tail_match = re.search(r'(?:tail|last)\s+(\d+)', lower)
        tail = int(tail_match.group(1)) if tail_match else 100
        if entity and entity not in ("for", "from", "of", "container"):
            return {"mode": "tool", "tool": "docker_logs", "args": {"container": entity, "tail": tail}}

    # --- Inspect ---
    if re.search(r'\binspect\b', lower):
        entity = _extract_entity(text, ["inspect container ", "inspect image ", "inspect "])
        if entity and entity not in ("container", "image"):
            return {"mode": "tool", "tool": "docker_inspect", "args": {"name": entity}}

    # --- Ports / which port ---
    if re.search(r'\bport(s)?\b', lower) and re.search(r'\b(which|what|show|get|check)\b', lower):
        entity = _extract_entity(text, ["container ", "for ", "of ", "port "])
        # Fallback: last word that looks like a container id or name
        if not entity or entity in ("is", "container", "running", "on"):
            for w in reversed(words):
                if len(w) >= 3 and w not in ("port", "ports", "which", "what", "show", "running", "container", "on", "is", "the", "for", "of", "get", "check"):
                    entity = w
                    break
        if entity:
            return {"mode": "tool", "tool": "docker_ports", "args": {"container": entity}}

    # --- Exec ---
    if re.search(r'\bexec\b', lower):
        # "exec ls in abc" or "execute 'ls -la' inside container abc"
        entity = _extract_entity(text, ["in container ", "inside container ", "in ", "inside "])
        cmd = _extract_entity(text, ["exec ", "execute "])
        if entity and cmd:
            return {"mode": "tool", "tool": "docker_exec", "args": {"container_id": entity, "command": cmd}}

    # --- Pull image ---
    if re.search(r'\b(pull|download|fetch)\b', lower):
        entity = _extract_entity(text, ["pull image ", "pull ", "download image ", "download ", "fetch image ", "fetch "])
        if entity and entity not in ("image", "the"):
            return {"mode": "tool", "tool": "docker_pull", "args": {"image_name": entity}}

    # --- Build (must come before Run to catch "run X.dockerfile" as build) ---
    # Detect dockerfile filenames like "python.dockerfile", "Dockerfile", "app.Dockerfile"
    dockerfile_match = re.search(r'(\S+\.dockerfile|Dockerfile)\b', text, re.IGNORECASE)
    if dockerfile_match or re.search(r'\bbuild\b', lower):
        args = {"path": "."}

        # Extract tag from "with name X", "tag X", "-t X", "as X"
        tag_match = re.search(r'(?:with\s+name|named|tag(?:ged)?|as|-t)\s+["\']?(\S+)["\']?', text, re.IGNORECASE)
        if tag_match:
            args["tag"] = tag_match.group(1).strip("'\"")

        # Extract dockerfile name
        if dockerfile_match:
            args["dockerfile"] = dockerfile_match.group(1)

        # Extract path if explicitly given
        path_match = re.search(r'(?:in|from|path|context)\s+(\S+)', lower)
        if path_match:
            args["path"] = path_match.group(1)

        return {"mode": "tool", "tool": "docker_build", "args": args}

    # --- Prune ---
    if re.search(r'\b(prune|cleanup|clean up|clean)\b', lower):
        rtype = "all"
        if "image" in lower:
            rtype = "image"
        elif "container" in lower:
            rtype = "container"
        elif "volume" in lower:
            rtype = "volume"
        elif "network" in lower:
            rtype = "network"
        return {"mode": "tool", "tool": "docker_prune", "args": {"resource_type": rtype}}

    # --- Run image ---
    if re.search(r'\b(run|start|launch|deploy)\b', lower):
        entity = _extract_entity(text, ["run image ", "run ", "start ", "launch ", "deploy "])
        if entity and entity not in ("container", "containers", "image", "a", "the", "an"):
            port = _extract_port(text)
            args = {"image": entity}
            if port:
                args["port"] = port
                # Check for explicit host:container syntax like "9999:8080"
                port_pair = re.search(r'(\d{2,5}):(\d{2,5})', text)
                if port_pair:
                    args["port"] = int(port_pair.group(1))
                    args["container_port"] = int(port_pair.group(2))
            return {"mode": "tool", "tool": "docker_run", "args": args}

    # --- Stats ---
    if re.search(r'\b(stats|resources|cpu|memory usage)\b', lower):
        entity = _extract_entity(text, ["stats for ", "stats of ", "stats ", "resources for ", "resources of "])
        return {"mode": "tool", "tool": "docker_stats", "args": {"container": entity} if entity else {}}

    # No match — return None so LLM handles it
    return None


def plan_action(user_input: str) -> Dict:
    """Plan action using fast rules first, then LLM fallback."""
    # Try deterministic fast planner first
    fast = _fast_plan(user_input)
    if fast:
        print(f"⚡ Fast plan: {fast.get('tool', fast.get('mode'))}")
        return fast

    # Fall back to LLM-based planner
    prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nJSON:"
    data = generate_json(prompt)
    
    # Validate the response has required fields
    if not data or data.get("mode") not in {"tool", "knowledge", "chat"}:
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
