"""
This is heavily based on work provided by Laxmikant Suryavanshi in this Medium article:
https://medium.com/@laxsuryavanshi.dev/production-grade-logging-for-fastapi-applications-a-complete-guide-f384d4b8f43b
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any, Sequence
from uuid import uuid4

import structlog
from starlette.datastructures import Headers
from starlette.types import Scope
from structlog.types import EventDict, Processor

# Thread-safe context storage
request_context: ContextVar[dict[str, Any]] = ContextVar("request_context")


def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one."""
    try:
        ctx = request_context.get()
        return ctx.get("correlation_id", str(uuid4()))
    except LookupError:
        return str(uuid4())


def set_correlation_id(correlation_id: str | None = None) -> str:
    """Set or generate a correlation ID for the current request."""
    cid = correlation_id or str(uuid4())
    try:
        ctx = request_context.get().copy()
    except LookupError:
        ctx = {}

    ctx["correlation_id"] = cid
    request_context.set(ctx)
    return cid


def bind_request_context(**kwargs: Any) -> None:
    """Bind additional context to the current request."""
    try:
        ctx = request_context.get().copy()
    except LookupError:
        ctx = {}

    ctx.update(kwargs)
    request_context.set(ctx)


def clear_request_context() -> None:
    """Clear the request context."""
    request_context.set({})


def add_request_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add request context to every log entry."""
    try:
        ctx = request_context.get()
        if ctx:
            event_dict.update(ctx)
    except LookupError:
        pass
    return event_dict


def configure_third_party_loggers(level: int) -> None:
    """Reduce noise from third-party libraries."""
    # Suppress verbose HTTP libraries
    for logger_name in ("httpcore", "httpx", "hpack", "urllib3"):
        logging.getLogger(logger_name).setLevel(max(level, logging.WARNING))

    # Configure Uvicorn loggers
    uvicorn_loggers = (
        ("uvicorn", level),
        ("uvicorn.error", level),
        ("uvicorn.access", max(level, logging.WARNING)),
    )

    for logger_name, log_level in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True  # Use root logger's handler
        logger.setLevel(log_level)


def configure_logging(log_json: bool, log_level: str):

    # Shared processors for both structlog and standard logging
    shared_processors: Sequence[Processor] = [
        add_request_context,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # JSON or console rendering
    if log_json:
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer: Processor = structlog.dev.ConsoleRenderer(
            colors=True, exception_formatter=structlog.dev.plain_traceback
        )

    # Structlog processor chain
    structlog_processors: Sequence[Processor] = [
        *shared_processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    # Standard library processor chain
    stdlib_processors: Sequence[Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        renderer,
    ]

    # Configure structlog
    structlog.configure(
        processors=structlog_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=stdlib_processors,
    )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    root_logger.addHandler(handler)

    configure_third_party_loggers(1)


def get_client_ip(scope: Scope, headers: Headers) -> str:
    """Extract client IP from headers or scope."""
    # Check X-Forwarded-For header (load balancer/proxy)
    if forwarded_for := headers.get("x-forwarded-for"):
        return forwarded_for.split(",", 1)[0].strip()

    # Check X-Real-IP header (nginx)a
    if real_ip := headers.get("x-real-ip"):
        return real_ip.strip()

    # Fall back to direct connection IP
    if client := scope.get("client"):
        return client[0]

    return "unknown"
