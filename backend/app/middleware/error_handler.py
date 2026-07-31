"""Global error handler middleware (pure ASGI).

Catches exceptions that escape the application (including routing and
dependency failures) and returns a clean JSON 500 response instead of
Starlette's plain-text "Internal Server Error" page. HTTPExceptions
raised by FastAPI are handled by Starlette before reaching this layer.

The error is logged with the request id for correlation, and the client
never receives internal details.
"""
import logging
import traceback
from typing import Callable

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("market_mind_ai.error")


class GlobalErrorHandlerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            request_id = scope.get("request_id", "-")
            path = scope.get("path", "-")
            logger.error(
                "Unhandled error on %s | request_id=%s\n%s",
                path,
                request_id,
                "".join(traceback.format_exception(exc)),
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
            await response(scope, receive, send)
