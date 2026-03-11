"""
Dockerfile generation and review with framework detection and template support.
Includes security scanning, compose templates, and environment file generation.
"""
from typing import Dict, Optional
from llm.ollama_client import generate
from prompts.dockerfile_prompt import DOCKERFILE_PROMPT
from prompts.dockerfile_templates import detect_template, get_template
from prompts.compose_templates import detect_compose_template, get_compose_template
from utils.security_scanner import scan_dockerfile_security, format_security_report
from utils.env_generator import get_env_file


def _is_dockerfile(text: str) -> bool:
    """Check if input contains Dockerfile syntax"""
    # Look for Dockerfile instructions - be very lenient to catch all variations
    markers = ["FROM", "RUN", "COPY", "ADD", "CMD", "ENTRYPOINT", "EXPOSE", "ENV", "WORKDIR", "USER"]
    upper_text = text.upper()
    
    # Count how many Dockerfile markers are present
    marker_count = sum(1 for marker in markers if marker in upper_text)
    
    # If 3+ Dockerfile instructions found, it's definitely a Dockerfile
    # (reduces false negatives when input is munged onto one line)
    return marker_count >= 3


def _detect_framework(text: str) -> str:
    """Detect framework/language from user input"""
    upper_text = text.upper()
    
    frameworks = {
        "PYTHON": ["PYTHON", "DJANGO", "FLASK", "FASTAPI", "UVICORN", "GUNICORN"],
        "NODE": ["NODE", "EXPRESS", "REACT", "NEXT", "NUXT", "NEST", "NPM", "YARN"],
        "GO": ["GO", "GOLANG", "GIN"],
        "JAVA": ["JAVA", "SPRING", "MAVEN", "GRADLE", "JAR"],
        "RUST": ["RUST", "CARGO"],
        ".NET": ["DOTNET", ".NET", "CSHARP", "ASPNET"],
        "PHP": ["PHP", "LARAVEL", "SYMFONY"],
        "RUBY": ["RUBY", "RAILS", "RACK"],
    }
    
    for framework, keywords in frameworks.items():
        if any(kw in upper_text for kw in keywords):
            return framework
    
    return "General"


def handle_dockerfile_request(user_input: str) -> Dict:
    """
    Generate or review a Dockerfile based on user input.
    
    SMART ROUTING:
    - Simple generation (Flask, Express, etc.) → Use template (0.5s) ✨ INSTANT
    - Complex/Custom request → Use LLM (45s) 
    - Review mode → Use LLM (analyzes issues)
    
    Returns a dict with display text and metadata.
    """
    mode = "review" if _is_dockerfile(user_input) else "generate"
    framework = _detect_framework(user_input)
    
    # Try template first if it's generation mode (not review)
    if mode == "generate":
        template_match = detect_template(user_input)
        if template_match:
            key, _func = template_match
            response = get_template(key)
            if response:
                return {
                    "mode": "dockerfile",
                    "display": response,
                    "dockerfile_mode": mode,
                    "framework": framework,
                    "source": "template",  # Mark as from template
                }
    
    # Fall back to LLM for review or complex generation
    if mode == "review":
        # REVIEW MODE: Make it crystal clear the user is providing a Dockerfile to analyze
        prompt = (
            f"{DOCKERFILE_PROMPT}\n"
            f"\n{'='*80}\n"
            f"🔍 DOCKERFILE REVIEW REQUEST\n"
            f"{'='*80}\n"
            f"Framework detected: {framework}\n\n"
            f"CRITICAL INSTRUCTION: The user has provided a Dockerfile BELOW for you to review.\n"
            f"Your task is to ANALYZE THIS DOCKERFILE and provide:\n"
            f"1. Issues found (security, best practices, performance)\n"
            f"2. Suggestions for improvement\n"
            f"3. Corrected version if major issues exist\n\n"
            f"THE DOCKERFILE TO REVIEW:\n"
            f"{'-'*80}\n"
            f"{user_input}\n"
            f"{'-'*80}\n\n"
            f"Your analysis:\n"
        )
    else:
        # GENERATION MODE: Standard prompt for creating Dockerfiles
        prompt = (
            f"{DOCKERFILE_PROMPT}\n"
            f"\n{'='*80}\n"
            f"DOCKERFILE GENERATION REQUEST\n"
            f"{'='*80}\n"
            f"Framework/Language detected: {framework}\n\n"
            f"User requirements:\n{user_input}\n\n"
            f"Generated Dockerfile:\n"
        )
    
    response = generate(prompt).strip()
    
    # Add security scan to review mode
    security_scan = None
    if mode == "review":
        # Check if header already exists in response (from LLM)
        if not response.startswith("🔍"):
            response = (
                "🔍 DOCKERFILE REVIEW\n" +
                response
            )
        
        # Add security scan
        security_scan = scan_dockerfile_security(user_input)
        security_report = format_security_report(security_scan)
        response += "\n\n" + security_report
    
    # Try to suggest docker-compose template for generation mode
    compose_template = None
    env_file = None
    if mode == "generate":
        compose_match = detect_compose_template(user_input)
        if compose_match:
            key, _func = compose_match
            compose_template = get_compose_template(key)
            env_file = get_env_file(key)
    
    result = {
        "mode": "dockerfile",
        "display": response,
        "dockerfile_mode": mode,
        "framework": framework,
        "source": "llm",  # Mark as from LLM
    }
    
    # Add optional related files
    if compose_template:
        result["compose"] = compose_template
        result["compose_available"] = True
    
    if env_file:
        result["env"] = env_file
        result["env_available"] = True
    
    if security_scan:
        result["security_scan"] = security_scan
    
    return result
