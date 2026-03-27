import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import structlog

# ContextVar accessible anywhere in the call stack
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


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
