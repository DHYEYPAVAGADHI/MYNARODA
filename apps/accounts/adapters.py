"""
Accounts App — Allauth Adapters
=================================
Custom adapters hook into django-allauth's flow to apply
our business logic during authentication and social login.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for email/password authentication.

    Overrides:
        - is_open_for_signup: Allow or block new registrations
        - get_login_redirect_url: Custom post-login redirect
    """

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """Allow signup. Can be toggled via settings for invite-only mode."""
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """Redirect to dashboard after login."""
        return "/"

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        """Redirect to home after logout."""
        return "/"


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social (Google) authentication.

    Overrides:
        - is_open_for_signup: Match our registration policy
        - populate_user: Set our custom fields from Google profile data
    """

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request, sociallogin, data):
        """
        Called when a new user registers via Google.
        Populates our custom User fields from the Google profile.
        """
        user = super().populate_user(request, sociallogin, data)

        # Set full_name from Google's name field
        if not user.full_name and data.get("name"):
            user.full_name = data["name"]

        # Mark email as verified since Google already verified it
        user.is_verified = True

        return user
