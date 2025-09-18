"""
Advanced Redis caching system
"""
import json
import pickle
import hashlib
import time
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis
from ..utils.logger import setup_module_logger


class CacheEntry:
    """Cache entry with metadata"""

    def __init__(self, key: str, value: Any, ttl: Optional[int] = None,
                 tags: Optional[List[str]] = None):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.tags = tags or []
        self.created_at = time.time()
        self.access_count = 0
        self.last_accessed = time.time()
        self.size_bytes = self._calculate_size()

    def _calculate_size(self) -> int:
        """Calculate approximate size in bytes"""
        try:
            if isinstance(self.value, (str, int, float, bool)):
                return len(str(self.value).encode('utf-8'))
            elif isinstance(self.value, (list, dict)):
                return len(json.dumps(self.value).encode('utf-8'))
            else:
                return len(pickle.dumps(self.value))
        except:
            return 1024  # Default estimate

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self):
        """Record access"""
        self.access_count += 1
        self.last_accessed = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key': self.key,
            'value': self.value,
            'ttl': self.ttl,
            'tags': self.tags,
            'created_at': self.created_at,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'size_bytes': self.size_bytes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        entry = cls(
            key=data['key'],
            value=data['value'],
            ttl=data.get('ttl'),
            tags=data.get('tags', [])
        )
        entry.created_at = data.get('created_at', time.time())
        entry.access_count = data.get('access_count', 0)
        entry.last_accessed = data.get('last_accessed', time.time())
        entry.size_bytes = data.get('size_bytes', 0)
        return entry


class RedisCacheManager:
    """Advanced Redis cache manager with clustering and monitoring"""

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 password: Optional[str] = None, db: int = 0,
                 max_connections: int = 20, enable_monitoring: bool = True):
        self.logger = setup_module_logger("redis_cache")
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.max_connections = max_connections
        self.enable_monitoring = enable_monitoring

        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False

        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'bytes_used': 0
        }

        # Tag index for efficient tag-based operations
        self.tag_index: Dict[str, set] = {}

        self._connect()

    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                decode_responses=False,  # We'll handle serialization
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )

            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            self.logger.info(f"Connected to Redis at {self.host}:{self.port}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
            # Continue without Redis - fallback to in-memory cache
            self._fallback_cache: Dict[str, CacheEntry] = {}

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key with namespace"""
        return f"vss_cache:{key}"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Redis storage"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return json.dumps(value).encode('utf-8')
            else:
                return pickle.dumps(value)
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")
            return pickle.dumps(str(value))

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from Redis"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except:
            # Fall back to pickle
            try:
                return pickle.loads(data)
            except Exception as e:
                self.logger.error(f"Deserialization error: {e}")
                return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            tags: Optional[List[str]] = None) -> bool:
        """Set cache entry"""

        if not self.is_connected and not hasattr(self, '_fallback_cache'):
            return False

        try:
            cache_key = self._get_cache_key(key)
            entry = CacheEntry(key, value, ttl, tags)

            if self.is_connected:
                # Store in Redis
                data = self._serialize_value(entry.to_dict())
                if ttl:
                    self.redis_client.setex(cache_key, ttl, data)
                else:
                    self.redis_client.set(cache_key, data)

                # Update tag index
                self._update_tag_index(key, tags or [])

            else:
                # Store in fallback cache
                self._fallback_cache[cache_key] = entry

            self.stats['sets'] += 1
            self.stats['bytes_used'] += entry.size_bytes

            return True

        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
            self.stats['errors'] += 1
            return False

    def get(self, key: str) -> Any:
        """Get cache entry"""

        if not self.is_connected and not hasattr(self, '_fallback_cache'):
            self.stats['misses'] += 1
            return None

        try:
            cache_key = self._get_cache_key(key)

            if self.is_connected:
                data = self.redis_client.get(cache_key)
                if not data:
                    self.stats['misses'] += 1
                    return None

                entry_dict = self._deserialize_value(data)
                if not entry_dict or not isinstance(entry_dict, dict):
                    self.stats['misses'] += 1
                    return None

                entry = CacheEntry.from_dict(entry_dict)

                # Check expiration
                if entry.is_expired():
                    self.delete(key)  # Clean up expired entry
                    self.stats['misses'] += 1
                    return None

                entry.access()
                self.stats['hits'] += 1

                # Update in Redis
                self.set(key, entry.value, entry.ttl, entry.tags)

                return entry.value

            else:
                # Get from fallback cache
                if cache_key in self._fallback_cache:
                    entry = self._fallback_cache[cache_key]
                    if entry.is_expired():
                        del self._fallback_cache[cache_key]
                        self.stats['misses'] += 1
                        return None

                    entry.access()
                    self.stats['hits'] += 1
                    return entry.value

                self.stats['misses'] += 1
                return None

        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            self.stats['errors'] += 1
            self.stats['misses'] += 1
            return None

    def delete(self, key: str) -> bool:
        """Delete cache entry"""

        if not self.is_connected and not hasattr(self, '_fallback_cache'):
            return False

        try:
            cache_key = self._get_cache_key(key)

            if self.is_connected:
                result = self.redis_client.delete(cache_key)
                if result > 0:
                    # Remove from tag index
                    self._remove_from_tag_index(key)
                    self.stats['deletes'] += 1
                    return True
            else:
                if cache_key in self._fallback_cache:
                    del self._fallback_cache[cache_key]
                    self.stats['deletes'] += 1
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Cache delete error: {e}")
            self.stats['errors'] += 1
            return False

    def clear_by_tag(self, tag: str) -> int:
        """Clear all cache entries with specific tag"""
        if not self.is_connected:
            return 0

        try:
            if tag in self.tag_index:
                keys_to_delete = list(self.tag_index[tag])
                deleted_count = 0

                for key in keys_to_delete:
                    if self.delete(key):
                        deleted_count += 1

                self.logger.info(f"Cleared {deleted_count} entries with tag '{tag}'")
                return deleted_count

            return 0

        except Exception as e:
            self.logger.error(f"Clear by tag error: {e}")
            return 0

    def clear_all(self) -> bool:
        """Clear all cache entries"""

        try:
            if self.is_connected:
                # Clear Redis keys with our namespace
                keys = self.redis_client.keys("vss_cache:*")
                if keys:
                    self.redis_client.delete(*keys)

                # Clear tag index
                self.tag_index.clear()

            elif hasattr(self, '_fallback_cache'):
                self._fallback_cache.clear()

            self.logger.info("Cache cleared")
            return True

        except Exception as e:
            self.logger.error(f"Clear all error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        stats = self.stats.copy()
        stats.update({
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'connected': self.is_connected,
            'tag_count': len(self.tag_index),
            'redis_info': self._get_redis_info() if self.is_connected else None
        })

        return stats

    def _get_redis_info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        try:
            info = self.redis_client.info()
            return {
                'version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory': info.get('used_memory'),
                'total_connections_received': info.get('total_connections_received'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except:
            return {}

    def _update_tag_index(self, key: str, tags: List[str]):
        """Update tag index for efficient tag-based operations"""
        for tag in tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(key)

    def _remove_from_tag_index(self, key: str):
        """Remove key from tag index"""
        for tag_keys in self.tag_index.values():
            tag_keys.discard(key)

        # Clean up empty tag sets
        self.tag_index = {tag: keys for tag, keys in self.tag_index.items() if keys}

    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        health = {
            'healthy': False,
            'response_time': None,
            'error': None
        }

        try:
            start_time = time.time()

            if self.is_connected:
                self.redis_client.ping()
            else:
                # For fallback cache, just check if it exists
                hasattr(self, '_fallback_cache')

            health['healthy'] = True
            health['response_time'] = time.time() - start_time

        except Exception as e:
            health['error'] = str(e)

        return health


# Global cache manager instance
cache_manager = RedisCacheManager()


def get_cache_manager() -> RedisCacheManager:
    """Get global cache manager instance"""
    return cache_manager


# Cache decorators
def cached(ttl: Optional[int] = None, tags: Optional[List[str]] = None):
    """Decorator for caching function results"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

            # Try to get from cache
            result = cache_manager.get(key)
            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache_manager.set(key, result, ttl, tags)

            return result

        return wrapper

    return decorator


def cache_invalidate_tag(tag: str):
    """Invalidate all cache entries with specific tag"""
    cache_manager.clear_by_tag(tag)


def cache_invalidate_all():
    """Invalidate all cache entries"""
    cache_manager.clear_all()