"""
Caching utilities for API responses and embeddings.
"""
import json
import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta
from app.utils.logger import logger


class SimpleCache:
    """Simple file-based cache with expiration."""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check expiration
            if datetime.now() - cached_data['timestamp'] > self.ttl:
                logger.debug(f"Cache expired for key: {key[:50]}...")
                cache_path.unlink()
                return None
            
            logger.debug(f"Cache hit for key: {key[:50]}...")
            return cached_data['value']
        
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, key: str, value: Any):
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cached_data = {
                'timestamp': datetime.now(),
                'value': value
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            
            logger.debug(f"Cached value for key: {key[:50]}...")
        
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear(self):
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("Cache cleared")


# Global cache instance
cache = SimpleCache()
