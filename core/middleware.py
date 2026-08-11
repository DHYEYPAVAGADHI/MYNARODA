"""
Core Middleware
================
Custom middleware for request logging, performance monitoring, and security.

Middleware Order (applied top-to-bottom on request, bottom-to-top on response):
    1. RequestLoggingMiddleware — logs every request with timing info

Each middleware class has exactly one responsibility.
"""

import logging
import time

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("core.middleware")


class RequestLoggingMiddleware:
    """
    Logs every HTTP request with:
        - Method, path, status code
        - Response time in milliseconds
        - Authenticated user (if any)

    Skips static file requests to avoid log noise.
    This enables performance monitoring and audit trail at the request level.
    """

    # Prefixes to exclude from logging (to keep logs clean)
    SKIP_PREFIXES = ("/static/", "/media/", "/favicon.ico", "/__debug__/")

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip irrelevant paths
        if any(request.path.startswith(prefix) for prefix in self.SKIP_PREFIXES):
            return self.get_response(request)

        start_time = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        user = getattr(request, "user", None)
        user_info = f"user={user.id}" if user and user.is_authenticated else "anon"

        logger.info(
            "%s %s %s %.2fms [%s]",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            user_info,
        )

        return response
