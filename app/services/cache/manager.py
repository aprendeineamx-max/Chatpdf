import redis
import logging
import hashlib
import json
from cachetools import TTLCache
from app.core.config import settings

logger = logging.getLogger(__name__)

class UnifiedCacheMode:
    REDIS = "REDIS"
    MEMORY = "MEMORY"

class CacheManager:
    def __init__(self):
        self.mode = UnifiedCacheMode.MEMORY
        self.redis_client = None
        self.memory_cache = TTLCache(maxsize=1000, ttl=300) # 5 Minute Default
        
        # Try connect Redis
        try:
            pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
            r = redis.Redis(connection_pool=pool)
            r.ping()
            self.redis_client = r
            self.mode = UnifiedCacheMode.REDIS
            logger.info("🚀 Redis Cache ACTIVE and Connected!")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable ({e}). Fallback to fast In-Memory Cache.")
            self.mode = UnifiedCacheMode.MEMORY

    def _hash_key(self, key_str: str):
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, prefix: str, key_content: str):
        hashed = self._hash_key(key_content)
        final_key = f"{prefix}:{hashed}"
        
        try:
            if self.mode == UnifiedCacheMode.REDIS:
                val = self.redis_client.get(final_key)
                if val:
                    return json.loads(val)
                return None
            else:
                return self.memory_cache.get(final_key)
        except Exception as e:
            logger.error(f"Cache Read Error: {e}")
            return None

    def set(self, prefix: str, key_content: str, value: dict, ttl: int = 300):
        hashed = self._hash_key(key_content)
        final_key = f"{prefix}:{hashed}"
        
        try:
            if self.mode == UnifiedCacheMode.REDIS:
                self.redis_client.setex(final_key, ttl, json.dumps(value))
            else:
                self.memory_cache[final_key] = value
        except Exception as e:
            logger.error(f"Cache Write Error: {e}")

cache_manager = CacheManager()
