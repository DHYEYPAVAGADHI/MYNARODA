"""
Accounts App — URLs
===================
"""
from django.urls import path

from apps.accounts.views import (
    DashboardView,
    ProfileView,
    ResendOTPView,
    VerifyPhoneView,
)

app_name = "accounts"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("verify-phone/", VerifyPhoneView.as_view(), name="verify_phone"),
    path("verify-phone/resend/", ResendOTPView.as_view(), name="resend_otp"),
]
