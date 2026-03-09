import time
from unittest.mock import MagicMock, patch

import pytest

from app.core.rate_limiter import RateLimiter


class FakeRedis:
    """Minimal fake Redis for testing the rate limiter without a real server."""

    def __init__(self):
        self._store: dict = {}

    def pipeline(self):
        return FakePipeline(self)

    def zremrangebyscore(self, key, min_score, max_score):
        if key not in self._store:
            return 0
        self._store[key] = {
            m: s for m, s in self._store[key].items() if not (min_score <= s <= max_score)
        }
        return 0

    def zcard(self, key):
        if key not in self._store:
            return 0
        return len(self._store[key])

    def zadd(self, key, mapping):
        if key not in self._store:
            self._store[key] = {}
        self._store[key].update(mapping)

    def zrange(self, key, start, stop, withscores=False):
        if key not in self._store or not self._store[key]:
            return []
        items = sorted(self._store[key].items(), key=lambda x: x[1])
        sliced = items[start : stop + 1 if stop >= 0 else None]
        if withscores:
            return sliced
        return [m for m, _ in sliced]

    def expire(self, key, seconds):
        pass


class FakePipeline:
    def __init__(self, redis_instance: FakeRedis):
        self._redis = redis_instance
        self._commands: list = []

    def zremrangebyscore(self, key, min_score, max_score):
        self._commands.append(("zremrangebyscore", key, min_score, max_score))
        return self

    def zcard(self, key):
        self._commands.append(("zcard", key))
        return self

    def zadd(self, key, mapping):
        self._commands.append(("zadd", key, mapping))
        return self

    def expire(self, key, seconds):
        self._commands.append(("expire", key, seconds))
        return self

    def execute(self):
        results = []
        for cmd in self._commands:
            name = cmd[0]
            if name == "zremrangebyscore":
                results.append(self._redis.zremrangebyscore(cmd[1], cmd[2], cmd[3]))
            elif name == "zcard":
                results.append(self._redis.zcard(cmd[1]))
            elif name == "zadd":
                self._redis.zadd(cmd[1], cmd[2])
                results.append(1)
            elif name == "expire":
                results.append(True)
        self._commands = []
        return results


class TestRateLimiter:
    def test_allows_requests_under_limit(self):
        fake_redis = FakeRedis()
        limiter = RateLimiter(redis_client=fake_redis, max_requests=5, window_seconds=60)

        for _ in range(5):
            allowed, retry_after = limiter.is_allowed("user1")
            assert allowed is True
            assert retry_after == 0

    def test_blocks_requests_over_limit(self):
        fake_redis = FakeRedis()
        limiter = RateLimiter(redis_client=fake_redis, max_requests=3, window_seconds=60)

        for _ in range(3):
            allowed, _ = limiter.is_allowed("user1")
            assert allowed is True

        allowed, retry_after = limiter.is_allowed("user1")
        assert allowed is False
        assert retry_after > 0

    def test_resets_after_window_expires(self):
        fake_redis = FakeRedis()
        limiter = RateLimiter(redis_client=fake_redis, max_requests=2, window_seconds=1)

        for _ in range(2):
            allowed, _ = limiter.is_allowed("user1")
            assert allowed is True

        # Should be blocked
        allowed, _ = limiter.is_allowed("user1")
        assert allowed is False

        # Wait for window to expire
        time.sleep(1.1)

        allowed, retry_after = limiter.is_allowed("user1")
        assert allowed is True
        assert retry_after == 0

    def test_returns_correct_retry_after(self):
        fake_redis = FakeRedis()
        limiter = RateLimiter(redis_client=fake_redis, max_requests=1, window_seconds=30)

        allowed, _ = limiter.is_allowed("user1")
        assert allowed is True

        allowed, retry_after = limiter.is_allowed("user1")
        assert allowed is False
        assert 1 <= retry_after <= 31

    def test_fails_open_when_redis_is_down(self):
        limiter = RateLimiter(redis_client=None, max_requests=1, window_seconds=60)

        allowed, retry_after = limiter.is_allowed("user1")
        assert allowed is True
        assert retry_after == 0

    def test_fails_open_when_redis_raises_exception(self):
        broken_redis = MagicMock()
        broken_redis.pipeline.side_effect = Exception("Connection refused")

        limiter = RateLimiter(redis_client=broken_redis, max_requests=1, window_seconds=60)

        allowed, retry_after = limiter.is_allowed("user1")
        assert allowed is True
        assert retry_after == 0

    def test_different_users_have_separate_limits(self):
        fake_redis = FakeRedis()
        limiter = RateLimiter(redis_client=fake_redis, max_requests=2, window_seconds=60)

        # Use up user1's quota
        for _ in range(2):
            limiter.is_allowed("user1")

        allowed, _ = limiter.is_allowed("user1")
        assert allowed is False

        # user2 should still be allowed
        allowed, _ = limiter.is_allowed("user2")
        assert allowed is True
