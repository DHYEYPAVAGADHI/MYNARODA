"""
Accounts App — Views
=====================
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.events.models import EventRegistration
from apps.trees.models import Tree


from apps.certificates.models import Certificate
from apps.notifications.models import Notification
from apps.gallery.models import Photo


class DashboardView(LoginRequiredMixin, View):
    """
    User dashboard displayed after login.
    Shows the user's planted trees, upcoming events, certificates, and photos.
    """
    template_name = "account/dashboard.html"

    def get(self, request):
        user = request.user
        active_tab = request.GET.get("tab", "overview")

        user_trees = Tree.objects.filter(planted_by=user).select_related("species").order_by("-created_at")
        event_regs = EventRegistration.objects.filter(user=user).select_related("event").order_by("-created_at")
        user_photos = Photo.objects.filter(photographer=user).select_related("category").order_by("-created_at")
        user_certificates = Certificate.objects.filter(user=user).order_by("-issued_at")
        user_notifications = Notification.objects.filter(user=user).order_by("-created_at")

        # Mark notifications as read if notifications tab is visited
        if active_tab == "notifications":
            user_notifications.filter(is_read=False).update(is_read=True)

        # Tree count aggregation by verification status
        trees_total = user_trees.count()
        trees_verified = user_trees.filter(verification_status="VERIFIED").count()
        trees_pending = user_trees.filter(verification_status="PENDING").count()
        trees_rejected = user_trees.filter(verification_status="REJECTED").count()

        context = {
            "active_tab": active_tab,
            "trees": user_trees,
            "trees_total": trees_total,
            "trees_verified": trees_verified,
            "trees_pending": trees_pending,
            "trees_rejected": trees_rejected,
            "event_registrations": event_regs,
            "upcoming_events": [reg.event for reg in event_regs if reg.event.starts_at >= timezone.now() and not reg.is_cancelled],
            "photos": user_photos,
            "certificates": user_certificates,
            "notifications": user_notifications,
        }
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    """View and edit user profile."""
    template_name = "account/profile.html"
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        user = request.user
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        
        if full_name:
            user.full_name = full_name
        
        # If phone changes, reset verification
        if phone and phone != user.phone:
            user.phone = phone
            user.is_phone_verified = False
            
        user.save()
        messages.success(request, _("Profile updated successfully."))
        return redirect("accounts:profile")


class VerifyPhoneView(LoginRequiredMixin, View):
    """Verify phone via OTP."""
    template_name = "account/verify_otp.html"
    
    def get(self, request):
        if request.user.is_phone_verified:
            return redirect("accounts:profile")
        return render(request, self.template_name)
        
    def post(self, request):
        otp = request.POST.get("otp")
        # Dummy validation for dev
        if otp == "123456":
            request.user.is_phone_verified = True
            request.user.save()
            messages.success(request, _("Phone number verified successfully."))
            return redirect("accounts:profile")
            
        messages.error(request, _("Invalid OTP. Please try again."))
        return render(request, self.template_name)


class ResendOTPView(LoginRequiredMixin, View):
    """Resend OTP logic."""
    def post(self, request):
        # Trigger OTP send logic here
        messages.success(request, _("A new OTP has been sent to your phone."))
        return redirect("accounts:verify_phone")


from django.contrib.auth import login as auth_login
from apps.accounts.models import User, UserRole

class MockGoogleLoginView(View):
    """
    Development-mode Google OAuth simulator.
    Shows a professional account-chooser form.
    On POST: finds or creates a user with the submitted email, then logs them in.
    """

    template_name = "account/mock_google_login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").strip().lower()
        full_name = request.POST.get("full_name", "").strip()

        if not email:
            messages.error(request, _("Please enter a valid email address."))
            return render(request, self.template_name)

        # Derive a display name from email prefix if none provided
        if not full_name:
            full_name = email.split("@")[0].replace(".", " ").replace("_", " ").title()

        # Find or create the user with this email
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "role": UserRole.CITIZEN,
                "is_verified": True,
                "is_phone_verified": True,
                "is_active": True,
            }
        )

        if not created and full_name and user.full_name != full_name:
            user.full_name = full_name
            user.save(update_fields=["full_name"])

        if created:
            user.set_unusable_password()
            user.save()

        # Ensure allauth has a *verified* EmailAddress record so it never
        # redirects to the email confirmation flow.
        try:
            from allauth.account.models import EmailAddress
            EmailAddress.objects.get_or_create(
                user=user,
                email=email,
                defaults={"primary": True, "verified": True},
            )
            # If the record existed but was not verified, mark it now.
            EmailAddress.objects.filter(user=user, email=email).update(verified=True, primary=True)
        except Exception:
            pass  # allauth not installed or model not available — safe to skip

        # Log in via standard Django ModelBackend (bypasses allauth flow entirely)
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        messages.success(request, _("Welcome! You are now signed in as %(name)s.") % {"name": user.full_name})
        return redirect("accounts:dashboard")


