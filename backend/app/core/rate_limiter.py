import logging
import time
import uuid
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


class GlobalRateLimiter:
    """Global (shared) rate limiter using Redis sliding window counter.

    Unlike RateLimiter which tracks per-user, this uses a single shared key
    to enforce a global request budget (e.g. for third-party API quotas).
    """

    def __init__(
        self,
        redis_client: Any,
        max_requests: int,
        window_seconds: int,
        key: str = "global_rate_limit",
    ):
        self.redis_client = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key = key

    def is_allowed(self) -> bool:
        """Check if a request is allowed under the global limit.

        Returns:
            True if the request is allowed, False if the limit is exceeded.
        """
        if self.redis_client is None:
            return True

        try:
            now = time.time()
            window_start = now - self.window_seconds

            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(self.key, 0, window_start)
            pipe.zcard(self.key)
            results = pipe.execute()

            current_count = results[1]

            if current_count >= self.max_requests:
                return False

            member = f"{now}:{uuid.uuid4().hex[:8]}"
            pipe2 = self.redis_client.pipeline()
            pipe2.zadd(self.key, {member: now})
            pipe2.expire(self.key, self.window_seconds + 1)
            pipe2.execute()

            return True

        except Exception as e:
            logger.warning(f"Global rate limiter error, failing open: {e}")
            return True


class RateLimiter:
    """Per-user rate limiter using Redis sliding window counter (sorted sets)."""

    def __init__(
        self,
        redis_client: Any,
        max_requests: int,
        window_seconds: int,
        key_prefix: str = "rate_limit",
    ):
        self.redis_client = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix

    def _get_key(self, identifier: str) -> str:
        return f"{self.key_prefix}:{identifier}"

    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """Check if a request is allowed for the given identifier.

        Args:
            identifier: User ID or IP address.

        Returns:
            Tuple of (is_allowed, retry_after) where retry_after is seconds
            until the window resets. retry_after is 0 if the request is allowed.
        """
        if self.redis_client is None:
            return (True, 0)

        try:
            now = time.time()
            window_start = now - self.window_seconds
            key = self._get_key(identifier)

            pipe = self.redis_client.pipeline()
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current entries in window
            pipe.zcard(key)
            results = pipe.execute()

            current_count = results[1]

            if current_count >= self.max_requests:
                # Get the oldest entry to calculate retry_after
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = int(oldest_time + self.window_seconds - now) + 1
                    return (False, max(retry_after, 1))
                return (False, self.window_seconds)

            # Add current request
            member = f"{now}:{uuid.uuid4().hex[:8]}"
            pipe2 = self.redis_client.pipeline()
            pipe2.zadd(key, {member: now})
            pipe2.expire(key, self.window_seconds + 1)
            pipe2.execute()

            return (True, 0)

        except Exception as e:
            logger.warning(f"Rate limiter error, failing open: {e}")
            return (True, 0)
