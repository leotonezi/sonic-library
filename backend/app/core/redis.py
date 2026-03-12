import logging
from typing import Optional

import redis

from app.core.config import settings

logger = logging.getLogger("redis")

_redis_client: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    """Return a Redis client instance, or None if Redis is unavailable.

    Uses a module-level singleton so the connection is reused across calls.
    If Redis cannot be reached, logs a warning and returns None so the
    application can continue to operate without Redis.
    """
    global _redis_client

    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            _redis_client = None

    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        _redis_client = client
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis is unavailable: {e}")
        return None
