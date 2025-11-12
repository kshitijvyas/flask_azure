"""
Redis Cache Service
Handles caching operations using Azure Cache for Redis
"""
import json
import redis
import logging
from flask import current_app
import os

logger = logging.getLogger(__name__)


class CacheService:
    """Service for managing Redis cache operations"""
    
    def __init__(self):
        self.redis_client = None
        self.default_ttl = 300  # 5 minutes default cache time
    
    def _initialize(self):
        """Initialize Redis client connection"""
        if self.redis_client:
            return
        
        # Get Redis connection string from environment or config
        redis_url = os.environ.get('REDIS_URL')
        
        if not redis_url:
            logger.warning("Redis URL not configured. Caching disabled.")
            return
        
        try:
            # Azure Redis format: rediss://:<password>@<hostname>:6380/0?ssl_cert_reqs=required
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,  # Automatically decode responses to strings
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
    
    def get(self, key):
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value (dict/list) or None if not found
        """
        self._initialize()
        
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key, value, ttl=None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (dict/list/str)
            ttl: Time to live in seconds (default: 300)
        
        Returns:
            bool: True if successful
        """
        self._initialize()
        
        if not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key):
        """
        Delete key from cache
        
        Args:
            key: Cache key or pattern (e.g., 'user:*')
        
        Returns:
            int: Number of keys deleted
        """
        self._initialize()
        
        if not self.redis_client:
            return 0
        
        try:
            # If key contains wildcard, delete all matching keys
            if '*' in key:
                keys = self.redis_client.keys(key)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                return self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return 0
    
    def clear_pattern(self, pattern):
        """
        Clear all keys matching a pattern
        
        Args:
            pattern: Redis key pattern (e.g., 'user:*', 'department:*')
        
        Returns:
            int: Number of keys deleted
        """
        return self.delete(pattern)
    
    def exists(self, key):
        """Check if key exists in cache"""
        self._initialize()
        
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check error: {e}")
            return False


# Singleton instance
cache_service = CacheService()
