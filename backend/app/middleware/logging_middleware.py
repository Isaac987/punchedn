"""
This is heavily based on work provided by Laxmikant Suryavanshi in this Medium article:
https://medium.com/@laxsuryavanshi.dev/production-grade-logging-for-fastapi-applications-a-complete-guide-f384d4b8f43b
"""

import time

import structlog
from core.logger import (
    bind_request_context,
    clear_request_context,
    get_client_ip,
    set_correlation_id,
)
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class LoggingMiddleware:
    """ASGI middleware for logging HTTP requests and responses."""

    def __init__(self, app: ASGIApp, *, exclude_paths: set[str] | None = None) -> None:
        self.app = app
        self.exclude_paths = exclude_paths or set()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request metadata
        path = scope.get("path", "")
        method = scope.get("method", "")
        headers = Headers(scope=scope)

        # Set up correlation ID
        correlation_id = headers.get("x-correlation-id")
        correlation_id = set_correlation_id(correlation_id)

        # Extract client IP
        client_ip = get_client_ip(scope, headers)

        # Bind request context
        bind_request_context(
            correlation_id=correlation_id, method=method, path=path, client_ip=client_ip
        )

        should_log = path not in self.exclude_paths
        start_time = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]
                # Add correlation ID to response headers
                response_headers = list(message.get("headers", []))
                response_headers.append((b"x-correlation-id", correlation_id.encode()))
                message["headers"] = response_headers

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            if should_log:
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.exception(
                    "http_request_incoming",
                    status_code=500,
                    duration_ms=round(duration_ms, 2),
                    error_type=type(exc).__name__,
                )
            raise
        else:
            if should_log:
                duration_ms = (time.perf_counter() - start_time) * 1000
                query_string = scope.get("query_string", b"").decode() or None

                logger.info(
                    "http_request_incoming",
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    query_string=query_string,
                )
        finally:
            clear_request_context()
