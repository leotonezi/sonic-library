import structlog
import time
from enum import Enum
from typing import Any, Optional

from app.core.metrics import circuit_breaker_state as cb_state_gauge

logger = structlog.get_logger("circuit_breaker")

_CB_STATE_VALUES = {"closed": 0, "open": 1, "half_open": 2}


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Redis-backed circuit breaker with three states: CLOSED, OPEN, HALF_OPEN.

    State is stored in a Redis hash keyed by circuit name so it can be
    shared across workers.

    - CLOSED: normal operation, all calls permitted.
    - OPEN: calls are blocked.  After *recovery_timeout* seconds the circuit
      transitions to HALF_OPEN.
    - HALF_OPEN: one probe request is permitted.  Success → CLOSED,
      failure → OPEN.

    If Redis is unavailable the breaker *fails open* (permits all calls).
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int,
        recovery_timeout: int,
        redis_client: Any,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.redis_client = redis_client
        self._key = f"circuit_breaker:{name}"

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def _get_state(self) -> dict:
        """Read the full circuit state from Redis."""
        if self.redis_client is None:
            return {}
        try:
            data = self.redis_client.hgetall(self._key)
            return data if data else {}
        except Exception as e:
            logger.warning("circuit_breaker_redis_read_error", service=self.name, error=str(e))
            return {}

    def _set_state(self, state: str, failure_count: int, last_failure_time: float) -> None:
        if self.redis_client is None:
            return
        try:
            self.redis_client.hset(
                self._key,
                mapping={
                    "state": state,
                    "failure_count": str(failure_count),
                    "last_failure_time": str(last_failure_time),
                },
            )
        except Exception as e:
            logger.warning("circuit_breaker_redis_write_error", service=self.name, error=str(e))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_call_permitted(self) -> bool:
        """Return True if a call should be attempted."""
        if self.redis_client is None:
            return True

        try:
            data = self._get_state()
            state = data.get("state", CircuitState.CLOSED)

            if state == CircuitState.CLOSED:
                return True

            if state == CircuitState.OPEN:
                last_failure = float(data.get("last_failure_time", 0))
                if time.time() - last_failure >= self.recovery_timeout:
                    # Transition to HALF_OPEN – allow one probe
                    logger.warning("circuit_breaker_state_change", service=self.name, from_state="open", to_state="half_open")
                    cb_state_gauge.labels(service=self.name).set(_CB_STATE_VALUES["half_open"])
                    self._set_state(
                        CircuitState.HALF_OPEN,
                        int(data.get("failure_count", 0)),
                        last_failure,
                    )
                    return True
                return False

            if state == CircuitState.HALF_OPEN:
                # Allow one probe request
                return True

            return True  # unknown state → fail open

        except Exception as e:
            logger.warning("circuit_breaker_check_error", service=self.name, error=str(e))
            return True

    def record_success(self) -> None:
        """Record a successful call. Resets failure count; HALF_OPEN → CLOSED."""
        if self.redis_client is None:
            return

        try:
            data = self._get_state()
            old_state = data.get("state", CircuitState.CLOSED)

            if old_state == CircuitState.HALF_OPEN:
                logger.warning("circuit_breaker_state_change", service=self.name, from_state="half_open", to_state="closed")

            cb_state_gauge.labels(service=self.name).set(_CB_STATE_VALUES["closed"])
            self._set_state(CircuitState.CLOSED, 0, 0)

        except Exception as e:
            logger.warning("circuit_breaker_record_success_error", service=self.name, error=str(e))

    def record_failure(self) -> None:
        """Record a failed call.

        - CLOSED: increment failure count; open circuit if threshold reached.
        - HALF_OPEN: immediately transition back to OPEN.
        """
        if self.redis_client is None:
            return

        try:
            data = self._get_state()
            old_state = data.get("state", CircuitState.CLOSED)
            failure_count = int(data.get("failure_count", 0)) + 1
            now = time.time()

            if old_state == CircuitState.HALF_OPEN:
                logger.warning("circuit_breaker_state_change", service=self.name, from_state="half_open", to_state="open")
                cb_state_gauge.labels(service=self.name).set(_CB_STATE_VALUES["open"])
                self._set_state(CircuitState.OPEN, failure_count, now)
                return

            if failure_count >= self.failure_threshold:
                logger.warning("circuit_breaker_state_change", service=self.name, from_state="closed", to_state="open", failure_count=failure_count)
                cb_state_gauge.labels(service=self.name).set(_CB_STATE_VALUES["open"])
                self._set_state(CircuitState.OPEN, failure_count, now)
            else:
                self._set_state(
                    old_state if old_state else CircuitState.CLOSED,
                    failure_count,
                    now,
                )

        except Exception as e:
            logger.warning("circuit_breaker_record_failure_error", service=self.name, error=str(e))
