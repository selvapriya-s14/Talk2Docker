"""
Simple LRU cache for LLM responses to speed up common requests
"""
import hashlib
from collections import OrderedDict
from datetime import datetime, timedelta


class ResponseCache:
    """Cache LLM responses by prompt hash. Auto-expires after 24 hours."""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def _hash_prompt(self, prompt: str) -> str:
        """Hash entire prompt for cache key (including user input)"""
        # Use the full prompt to ensure different inputs have different cache keys
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> str | None:
        """Get cached response if exists and not expired"""
        key = self._hash_prompt(prompt)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        response, timestamp = self.cache[key]
        
        # Check if expired
        if datetime.now() - timestamp > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None
        
        # Move to end (LRU)
        self.cache.move_to_end(key)
        self.hits += 1
        return response
    
    def set(self, prompt: str, response: str) -> None:
        """Cache response"""
        key = self._hash_prompt(prompt)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = (response, datetime.now())
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }


# Global cache instance
response_cache = ResponseCache()
