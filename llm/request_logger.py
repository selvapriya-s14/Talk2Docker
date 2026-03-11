"""
Logging for request tracking and analytics
"""
import logging
import json
from datetime import datetime
from pathlib import Path

# Create logs directory if needed
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logger
logger = logging.getLogger("talk2docker")
logger.setLevel(logging.INFO)

# File handler
fh = logging.FileHandler(LOG_DIR / "talk2docker.log")
fh.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
fh.setFormatter(formatter)
logger.addHandler(fh)


def log_request(mode: str, user_input: str, framework: str = None) -> None:
    """Log an incoming user request"""
    logger.info(f"REQUEST | Mode: {mode} | Framework: {framework} | Input: {user_input[:80]}")


def log_response(mode: str, response_time: float, cache_hit: bool = False) -> None:
    """Log response details"""
    source = "CACHE" if cache_hit else "LLM"
    logger.info(f"RESPONSE | Mode: {mode} | Time: {response_time:.2f}s | Source: {source}")


def log_error(mode: str, error: str) -> None:
    """Log errors"""
    logger.error(f"ERROR | Mode: {mode} | {error}")


def log_stats(stats: dict) -> None:
    """Log cache/system statistics"""
    logger.info(f"STATS | {stats}")
