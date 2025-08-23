"""
Caching layer for MCP Server OpenAI.

Provides Redis-based and in-memory caching for expensive operations
with automatic fallback and cache invalidation.
"""

import asyncio
import hashlib
import json
import pickle
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional, Union

from .config import get_config
from .logging import get_logger

logger = get_logger("cache")

# Try to import Redis, fall back to in-memory cache if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")


class InMemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.logger = get_logger("memory_cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry["expires_at"] and datetime.now(timezone.utc) > entry["expires_at"]:
            del self.cache[key]
            return None
        
        entry["last_accessed"] = datetime.now(timezone.utc)
        return entry["value"]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        # Evict old entries if cache is full
        if len(self.cache) >= self.max_size:
            await self._evict_lru()
        
        expires_at = None
        if ttl:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        
        self.cache[key] = {
            "value": value,
            "created_at": datetime.now(timezone.utc),
            "last_accessed": datetime.now(timezone.utc),
            "expires_at": expires_at
        }
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self.get(key) is not None
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        if not self.cache:
            return
        
        # Sort by last accessed time
        sorted_keys = sorted(
            self.cache.keys(),
            key=lambda k: self.cache[k]["last_accessed"]
        )
        
        # Remove oldest 10% of entries
        evict_count = max(1, len(sorted_keys) // 10)
        for key in sorted_keys[:evict_count]:
            del self.cache[key]
        
        self.logger.debug(f"Evicted {evict_count} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now(timezone.utc)
        expired_count = 0
        
        for entry in self.cache.values():
            if entry["expires_at"] and now > entry["expires_at"]:
                expired_count += 1
        
        return {
            "type": "memory",
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "max_size": self.max_size
        }


class RedisCache:
    """Redis-based cache with async support."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = get_logger("redis_cache")
    
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                # Test connection
                await self.redis_client.ping()
                self.logger.info("Connected to Redis")
            except Exception as e:
                self.logger.error("Failed to connect to Redis", error=e)
                raise
        
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            client = await self._get_client()
            data = await client.get(key)
            
            if data is None:
                return None
            
            # Deserialize data
            return pickle.loads(data)
            
        except Exception as e:
            self.logger.error(f"Failed to get key '{key}' from Redis", error=e)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache."""
        try:
            client = await self._get_client()
            
            # Serialize data
            data = pickle.dumps(value)
            
            if ttl:
                await client.setex(key, ttl, data)
            else:
                await client.set(key, data)
                
        except Exception as e:
            self.logger.error(f"Failed to set key '{key}' in Redis", error=e)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete key '{key}' from Redis", error=e)
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        try:
            client = await self._get_client()
            await client.flushdb()
            
        except Exception as e:
            self.logger.error("Failed to clear Redis cache", error=e)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            client = await self._get_client()
            result = await client.exists(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to check key '{key}' in Redis", error=e)
            return False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            client = await self._get_client()
            info = await client.info("memory")
            
            return {
                "type": "redis",
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0)
            }
            
        except Exception as e:
            self.logger.error("Failed to get Redis stats", error=e)
            return {"type": "redis", "error": str(e)}


class CacheManager:
    """Unified cache manager with automatic fallback."""
    
    def __init__(self):
        self.config = get_config()
        self.primary_cache: Optional[Union[RedisCache, InMemoryCache]] = None
        self.fallback_cache = InMemoryCache(max_size=500)
        self.logger = get_logger("cache_manager")
        self._initialized = False
    
    async def _initialize(self) -> None:
        """Initialize cache backends."""
        if self._initialized:
            return
        
        if self.config.cache.enabled:
            if self.config.cache.redis_url and REDIS_AVAILABLE:
                try:
                    self.primary_cache = RedisCache(self.config.cache.redis_url)
                    # Test connection
                    await self.primary_cache.get("__test__")
                    self.logger.info("Using Redis as primary cache")
                except Exception as e:
                    self.logger.warning("Failed to initialize Redis cache, using memory cache", error=e)
                    self.primary_cache = InMemoryCache(max_size=1000)
            else:
                self.primary_cache = InMemoryCache(max_size=1000)
                self.logger.info("Using in-memory cache")
        else:
            self.logger.info("Caching is disabled")
        
        self._initialized = True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with fallback."""
        await self._initialize()
        
        if not self.config.cache.enabled:
            return None
        
        # Try primary cache first
        if self.primary_cache:
            try:
                value = await self.primary_cache.get(key)
                if value is not None:
                    return value
            except Exception as e:
                self.logger.warning(f"Primary cache get failed for key '{key}'", error=e)
        
        # Try fallback cache
        try:
            return await self.fallback_cache.get(key)
        except Exception as e:
            self.logger.error(f"Fallback cache get failed for key '{key}'", error=e)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with fallback."""
        await self._initialize()
        
        if not self.config.cache.enabled:
            return
        
        if ttl is None:
            ttl = self.config.cache.default_ttl
        
        # Set in primary cache
        if self.primary_cache:
            try:
                await self.primary_cache.set(key, value, ttl)
            except Exception as e:
                self.logger.warning(f"Primary cache set failed for key '{key}'", error=e)
        
        # Set in fallback cache
        try:
            await self.fallback_cache.set(key, value, ttl)
        except Exception as e:
            self.logger.error(f"Fallback cache set failed for key '{key}'", error=e)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        await self._initialize()
        
        if not self.config.cache.enabled:
            return False
        
        success = False
        
        # Delete from primary cache
        if self.primary_cache:
            try:
                success = await self.primary_cache.delete(key) or success
            except Exception as e:
                self.logger.warning(f"Primary cache delete failed for key '{key}'", error=e)
        
        # Delete from fallback cache
        try:
            success = await self.fallback_cache.delete(key) or success
        except Exception as e:
            self.logger.error(f"Fallback cache delete failed for key '{key}'", error=e)
        
        return success
    
    async def get_or_compute(
        self,
        key: str,
        compute_func: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """Get from cache or compute and store."""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            self.logger.debug(f"Cache hit for key '{key}'")
            return cached_value
        
        # Compute value
        self.logger.debug(f"Cache miss for key '{key}', computing value")
        
        if asyncio.iscoroutinefunction(compute_func):
            computed_value = await compute_func()
        else:
            computed_value = compute_func()
        
        # Store in cache
        await self.set(key, computed_value, ttl)
        
        return computed_value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        # This is a simplified implementation
        # In a real Redis setup, you'd use SCAN with pattern matching
        self.logger.info(f"Pattern invalidation not fully implemented: {pattern}")
        return 0
    
    def create_key(self, *args: Any) -> str:
        """Create a cache key from arguments."""
        # Create a deterministic key from arguments
        key_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        await self._initialize()
        
        stats = {
            "enabled": self.config.cache.enabled,
            "fallback_cache": await self.fallback_cache.get_stats()
        }
        
        if self.primary_cache:
            if isinstance(self.primary_cache, RedisCache):
                stats["primary_cache"] = await self.primary_cache.get_stats()
            else:
                stats["primary_cache"] = self.primary_cache.get_stats()
        
        return stats


# Global cache manager instance
_global_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _global_cache_manager


async def cached(
    key: str,
    compute_func: Callable[[], Any],
    ttl: Optional[int] = None
) -> Any:
    """Convenience function for caching."""
    return await _global_cache_manager.get_or_compute(key, compute_func, ttl)
