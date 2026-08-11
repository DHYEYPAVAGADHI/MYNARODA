"""
Core Custom Exceptions
========================
Standardised exception classes and a custom DRF exception handler.

All API error responses follow a consistent envelope:
    {
        "success": false,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Human-readable error description",
            "detail": { ... }  // Optional field-level errors
        }
    }

Usage:
    raise ServiceError("Something went wrong", code="PAYMENT_FAILED")
    raise PermissionDeniedError("You cannot delete another user's tree.")
"""

import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


# ─── Domain Exceptions ────────────────────────────────────────────────────────


class AppError(Exception):
    """
    Base exception for all application-layer errors.
    Never raise this directly — use a more specific subclass.
    """

    default_code = "APP_ERROR"
    default_message = "An unexpected error occurred."
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        detail: Any = None,
    ) -> None:
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.detail = detail
        super().__init__(self.message)


class ValidationError(AppError):
    """Raised when business-layer validation fails (distinct from DRF serializer validation)."""

    default_code = "VALIDATION_ERROR"
    http_status = status.HTTP_400_BAD_REQUEST


class NotFoundError(AppError):
    """Raised when a requested resource does not exist or has been soft-deleted."""

    default_code = "NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND


class PermissionDeniedError(AppError):
    """Raised when a user lacks permission to perform an action at the service layer."""

    default_code = "PERMISSION_DENIED"
    http_status = status.HTTP_403_FORBIDDEN


class ConflictError(AppError):
    """Raised when an operation would violate a uniqueness or state constraint."""

    default_code = "CONFLICT"
    http_status = status.HTTP_409_CONFLICT


class ServiceError(AppError):
    """Raised for unexpected failures within a service (e.g. external API failure)."""

    default_code = "SERVICE_ERROR"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE


class OTPError(AppError):
    """Raised when OTP verification fails."""

    default_code = "OTP_ERROR"
    http_status = status.HTTP_400_BAD_REQUEST


# ─── Custom Exception Handler ─────────────────────────────────────────────────


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Custom DRF exception handler.

    Converts all exceptions (both DRF native and our domain exceptions)
    into a consistent JSON envelope.

    Called by DRF when any exception propagates out of a view.
    Configured in settings.REST_FRAMEWORK.EXCEPTION_HANDLER.
    """
    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    if isinstance(exc, AppError):
        # Our domain exceptions — format consistently
        logger.warning(
            "Domain exception: code=%s message=%s",
            exc.code,
            exc.message,
            exc_info=True,
        )
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "detail": exc.detail,
                },
            },
            status=exc.http_status,
        )

    if response is not None:
        # DRF native exceptions — reformat into our envelope
        error_detail = response.data

        # Flatten DRF's error structure to our format
        if isinstance(error_detail, dict):
            first_key = next(iter(error_detail), "detail")
            first_value = error_detail.get(first_key, "An error occurred.")
            if isinstance(first_value, list):
                message = str(first_value[0])
            else:
                message = str(first_value)
        elif isinstance(error_detail, list):
            message = str(error_detail[0]) if error_detail else "An error occurred."
        else:
            message = str(error_detail)

        response.data = {
            "success": False,
            "error": {
                "code": "REQUEST_ERROR",
                "message": message,
                "detail": error_detail,
            },
        }
        return response

    # Unhandled exceptions — log and return 500
    logger.error("Unhandled exception in view", exc_info=True)
    return Response(
        {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "detail": None,
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
