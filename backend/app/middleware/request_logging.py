"""Request logging middleware (pure ASGI).

Logs a single access line per HTTP request after the response has
started: method, path, status code, duration, request id and client
address. Relies on RequestContextMiddleware having run first — it
populates ``scope["request_id"]`` and ``scope["request_duration_ms"]``.

Logs at INFO for 2xx/3xx/4xx and at ERROR for 5xx responses.
"""
import logging
import time
from typing import Callable

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import ACCESS_LOG_FORMAT

logger = logging.getLogger("market_mind_ai.access")

# Endpoints whose paths are never logged (avoid leaking secrets).
_SENSITIVE_PATHS = ("/auth/login", "/auth/token")


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        request_id = scope.get("request_id", "-")
        path = scope.get("path", "-")
        method = scope.get("method", "-")
        client = scope.get("client")
        client_ip = client[0] if client else "-"

        # Skip logging the body for sensitive endpoints.
        log_path = (
            "[REDACTED]" if path in _SENSITIVE_PATHS else path
        )

        status_code = 0
        error: BaseException | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            error = exc
            raise
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            extra = {
                "request_id": request_id,
                "duration_ms": duration_ms,
            }
            if status_code >= 500 or error is not None:
                logger.error(
                    "%s %s -> %s from %s",
                    method,
                    log_path,
                    status_code or "ERR",
                    client_ip,
                    exc_info=error is not None,
                    extra=extra,
                )
            else:
                logger.info(
                    "%s %s -> %s from %s",
                    method,
                    log_path,
                    status_code,
                    client_ip,
                    extra=extra,
                )
