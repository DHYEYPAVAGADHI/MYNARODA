"""
Core Custom Permissions
========================
Reusable DRF permission classes used across all apps.

Design:
    Each class has one clear responsibility.
    Permissions are composable via DRF's `|` and `&` operators.
    Never put business logic inside permission classes.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwner(BasePermission):
    """
    Allow access only to the owner of the resource.

    The view or model must define an `owner_field` attribute (default: 'user').
    """

    message = "You do not have permission to access this resource."

    def has_object_permission(self, request: Request, view: APIView, obj: object) -> bool:
        owner_field = getattr(view, "owner_field", "user")
        owner = getattr(obj, owner_field, None)
        return owner == request.user


class IsVerifiedUser(BasePermission):
    """Allow access only to users who have verified their email address."""

    message = "Please verify your email address before accessing this feature."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )


class HasRole(BasePermission):
    """
    Allow access only if the user has one of the required roles.

    Usage on a view:
        required_roles = ["VOLUNTEER", "ORGANIZER", "ADMIN"]
    """

    message = "You do not have the required role to perform this action."

    def has_permission(self, request: Request, view: APIView) -> bool:
        required_roles = getattr(view, "required_roles", [])
        if not required_roles:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in required_roles
        )


class IsAdminOrReadOnly(BasePermission):
    """
    SAFE methods (GET, HEAD, OPTIONS) are permitted for all authenticated users.
    Write methods (POST, PUT, PATCH, DELETE) require ADMIN or SUPER_ADMIN role.
    """

    ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user and request.user.is_authenticated
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ADMIN_ROLES
        )


class IsVolunteerOrAbove(BasePermission):
    """Permit VOLUNTEER, PHOTOGRAPHER, COORDINATOR, ORGANIZER, ADMIN, SUPER_ADMIN."""

    PERMITTED_ROLES = {
        "VOLUNTEER",
        "PHOTOGRAPHER",
        "COORDINATOR",
        "ORGANIZER",
        "ADMIN",
        "SUPER_ADMIN",
    }

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.PERMITTED_ROLES
        )


class IsSuperAdmin(BasePermission):
    """Restrict access to SUPER_ADMIN only."""

    message = "This action requires Super Admin privileges."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "SUPER_ADMIN"
        )
