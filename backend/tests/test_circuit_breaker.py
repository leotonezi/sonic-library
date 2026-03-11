import time
from unittest.mock import MagicMock

import pytest

from app.core.circuit_breaker import CircuitBreaker, CircuitState


class FakeRedisHash:
    """Minimal fake Redis supporting hash operations for circuit breaker tests."""

    def __init__(self):
        self._store: dict = {}

    def hgetall(self, key):
        return dict(self._store.get(key, {}))

    def hset(self, key, mapping=None, **kwargs):
        if key not in self._store:
            self._store[key] = {}
        if mapping:
            self._store[key].update(mapping)


class TestCircuitBreaker:
    def _make_cb(self, redis_client=None, threshold=3, timeout=5):
        if redis_client is None:
            redis_client = FakeRedisHash()
        return CircuitBreaker(
            name="test",
            failure_threshold=threshold,
            recovery_timeout=timeout,
            redis_client=redis_client,
        )

    def test_starts_closed_and_permits_calls(self):
        cb = self._make_cb()
        assert cb.is_call_permitted() is True

    def test_opens_after_n_failures(self):
        cb = self._make_cb(threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.is_call_permitted() is False

    def test_stays_closed_below_threshold(self):
        cb = self._make_cb(threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_call_permitted() is True

    def test_blocks_calls_when_open(self):
        cb = self._make_cb(threshold=1)
        cb.record_failure()
        assert cb.is_call_permitted() is False
        assert cb.is_call_permitted() is False

    def test_half_opens_after_timeout(self):
        cb = self._make_cb(threshold=1, timeout=1)
        cb.record_failure()
        assert cb.is_call_permitted() is False

        time.sleep(1.1)
        # Should transition to HALF_OPEN and allow one probe
        assert cb.is_call_permitted() is True

    def test_closes_on_successful_probe(self):
        cb = self._make_cb(threshold=1, timeout=1)
        cb.record_failure()
        time.sleep(1.1)

        # Transition to HALF_OPEN
        assert cb.is_call_permitted() is True
        cb.record_success()

        # Should now be CLOSED – all calls permitted
        assert cb.is_call_permitted() is True
        assert cb.is_call_permitted() is True

    def test_reopens_on_failed_probe(self):
        cb = self._make_cb(threshold=1, timeout=1)
        cb.record_failure()
        time.sleep(1.1)

        # Transition to HALF_OPEN
        assert cb.is_call_permitted() is True
        cb.record_failure()

        # Should be OPEN again
        assert cb.is_call_permitted() is False

    def test_fails_open_when_redis_is_none(self):
        cb = CircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=5,
            redis_client=None,
        )
        assert cb.is_call_permitted() is True
        cb.record_failure()  # should not raise
        cb.record_success()  # should not raise
        assert cb.is_call_permitted() is True

    def test_fails_open_when_redis_raises(self):
        broken = MagicMock()
        broken.hgetall.side_effect = Exception("Connection refused")

        cb = CircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=5,
            redis_client=broken,
        )
        assert cb.is_call_permitted() is True

    def test_record_success_resets_failure_count(self):
        cb = self._make_cb(threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        # After reset, should need 3 more failures to open
        cb.record_failure()
        cb.record_failure()
        assert cb.is_call_permitted() is True
        cb.record_failure()
        assert cb.is_call_permitted() is False
