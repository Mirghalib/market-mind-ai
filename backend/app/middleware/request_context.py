"""Request ID + timing middleware (pure ASGI).

Assigns a unique request id (from the X-Request-ID header or a uuid4),
exposes it to the request scope, and records request duration. The id
can be read inside handlers via:

    request.scope["request_id"]
"""
import time
import uuid
from typing import Callable

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        request_id = (
            headers.get(b"x-request-id", b"").decode()
            or str(uuid.uuid4())
        )
        scope["request_id"] = request_id
        start_time = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Request-ID", request_id)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            scope["request_duration_ms"] = round(duration_ms, 2)
