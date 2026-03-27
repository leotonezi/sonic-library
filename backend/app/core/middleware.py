import time
import uuid
from contextvars import ContextVar
from typing import Optional

from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import structlog

from app.core.config import settings

# ContextVar accessible anywhere in the call stack
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

logger = structlog.get_logger("middleware")

# Paths excluded from request logging to reduce noise
_EXCLUDED_PATHS: set[str] = {"/health", "/readiness", "/liveness", "/metrics"}


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request_id to every request.

    • Reuses an incoming ``X-Request-ID`` header when present.
    • Stores the value in a ``ContextVar`` so any code (including structlog
      processors) can read it without explicit parameter passing.
    • Returns the ``X-Request-ID`` header on the response.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        request_id_ctx.set(rid)

        # Bind to structlog contextvars so every log line includes request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=rid)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response


def _extract_user_id(request: Request) -> Optional[str]:
    """Extract user email from JWT cookie without hitting the database."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request/response with method, path, status, and duration.

    • INFO for 2xx/3xx, WARNING for 4xx, ERROR for 5xx.
    • Health-check paths are excluded to reduce noise.
    • Extracts user_id from JWT cookie (lightweight, no DB hit).
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        # Skip excluded paths (health checks, etc.)
        if path in _EXCLUDED_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        user_id = _extract_user_id(request)
        status_code = response.status_code

        log_kwargs = dict(
            method=request.method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
        )

        if status_code >= 500:
            logger.error("request completed", **log_kwargs)
        elif status_code >= 400:
            logger.warning("request completed", **log_kwargs)
        else:
            logger.info("request completed", **log_kwargs)

        return response
