"""
Admin Authentication — Custom Login + OTP Verification
=======================================================
Two-factor authentication for the admin panel.

Flow:
  1. Admin enters email + password → credentials verified
  2. 6-digit OTP generated and sent to registered mobile (9898143222)
  3. Admin enters OTP on the verify screen → session granted

OTP Delivery:
  - Primary: SMS to the fixed admin mobile 9898143222
  - Fallback: Printed to Django console (for development)
  - Also sent via email as backup
"""
import secrets
import logging
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from apps.accounts.models import User, OTPToken, OTPPurpose, DeviceFingerprint, AdminAuditLog

logger = logging.getLogger(__name__)

# ── Admin OTP Configuration ────────────────────────────────────────
# The fixed admin mobile number that receives all admin OTPs.
ADMIN_OTP_MOBILE = "9898143222"
ADMIN_OTP_MOBILE_FORMATTED = "+919898143222"


def _send_admin_otp_sms(mobile: str, code: str) -> bool:
    """
    Send OTP via SMS to the admin mobile number.

    In development: prints OTP to console (Django logs).
    In production: integrate with Twilio / MSG91 / Fast2SMS here.

    Returns True if sent successfully.
    """
    message = (
        f"GREEN NARODA ADMIN OTP\n"
        f"Your verification code is: {code}\n"
        f"Valid for 5 minutes. Do not share.\n"
        f"— Green Naroda • Clean Naroda"
    )

    # ── Console output (always, for dev visibility) ────────────────
    logger.info("=" * 55)
    logger.info(f"  ADMIN OTP FOR MOBILE: {mobile}")
    logger.info(f"  CODE: {code}")
    logger.info("=" * 55)

    # Print to terminal (visible in runserver output)
    print("\n" + "=" * 55)
    print(f"  🔐 ADMIN OTP FOR: {mobile}")
    print(f"  📱 CODE: {code}")
    print(f"  ⏱  Expires in 5 minutes")
    print("=" * 55 + "\n")

    # ── Production SMS Integration ─────────────────────────────────
    # Uncomment and configure your SMS provider below:
    #
    # Option 1: MSG91 (popular in India)
    # import requests
    # r = requests.post("https://api.msg91.com/api/v5/otp", json={
    #     "authkey": settings.MSG91_AUTH_KEY,
    #     "mobile": mobile,
    #     "otp": code,
    #     "template_id": settings.MSG91_OTP_TEMPLATE_ID,
    # })
    # return r.status_code == 200
    #
    # Option 2: Fast2SMS (budget Indian SMS)
    # import requests
    # r = requests.post("https://www.fast2sms.com/dev/bulkV2", headers={
    #     "authorization": settings.FAST2SMS_API_KEY
    # }, data={
    #     "variables_values": code,
    #     "route": "otp",
    #     "numbers": mobile,
    # })
    # return r.status_code == 200
    #
    # Option 3: Twilio
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    # client.messages.create(
    #     body=message, from_=settings.TWILIO_FROM, to=f"+91{mobile}"
    # )

    return True


class CustomAdminLoginView(LoginView):
    template_name = "admin/login.html"

    def form_valid(self, form):
        """Intercept login — verify credentials but do NOT log in yet."""
        user = form.get_user()

        # Only admin/staff users allowed
        if not (user.is_staff or user.is_superuser):
            return super().form_invalid(form)

        # Generate 6-digit OTP
        code = f"{secrets.randbelow(1000000):06d}"
        expires_at = timezone.now() + timedelta(minutes=5)

        # Invalidate all previous unused tokens
        OTPToken.objects.filter(
            user=user,
            purpose=OTPPurpose.ADMIN_LOGIN,
            is_used=False
        ).update(expires_at=timezone.now())

        # Save new OTP token
        OTPToken.objects.create(
            user=user,
            purpose=OTPPurpose.ADMIN_LOGIN,
            code=code,
            expires_at=expires_at,
        )

        # ── Send OTP to fixed admin mobile ────────────────────────
        _send_admin_otp_sms(ADMIN_OTP_MOBILE, code)

        # ── Also send via email as backup ─────────────────────────
        try:
            send_mail(
                subject="[Green Naroda Admin] Your OTP Code",
                message=(
                    f"Green Naroda • Clean Naroda — Government Portal\n\n"
                    f"Your Admin Login OTP: {code}\n\n"
                    f"This code expires in 5 minutes.\n"
                    f"If you did not request this, ignore this email.\n\n"
                    f"— Green Naroda Security System"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Admin OTP email failed: {e}")

        # Store user ID in session for OTP step
        self.request.session['pre_2fa_user_id'] = str(user.id)

        # Audit log
        AdminAuditLog.objects.create(
            user=user,
            action=AdminAuditLog.ActionType.LOGIN,
            details=f"Password verified. OTP sent to mobile {ADMIN_OTP_MOBILE}.",
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return HttpResponseRedirect(reverse('admin_otp_verify'))


class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label=_("Verification Code"),
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'autocomplete': 'one-time-code'}),
    )


class OTPVerifyView(FormView):
    template_name = "admin/otp_verify.html"
    form_class = OTPVerifyForm

    def get_user(self):
        user_id = self.request.session.get('pre_2fa_user_id')
        if not user_id:
            return None
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        if not self.get_user():
            return redirect('admin:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib import admin as django_admin
        context.update(django_admin.site.each_context(self.request))
        context['title'] = "Verify OTP"
        context['admin_mobile'] = ADMIN_OTP_MOBILE
        return context

    def form_valid(self, form):
        user = self.get_user()
        code = form.cleaned_data['code'].strip()

        token = OTPToken.objects.filter(
            user=user,
            purpose=OTPPurpose.ADMIN_LOGIN,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()

        if not token:
            form.add_error("code", "⚠️ Invalid or expired OTP. Please try again.")
            AdminAuditLog.objects.create(
                user=user,
                action=AdminAuditLog.ActionType.OTP_FAILURE,
                details=f"Failed OTP attempt. Code entered: {code}",
                ip_address=self.request.META.get("REMOTE_ADDR"),
            )
            return self.form_invalid(form)

        # Mark token used
        token.is_used = True
        token.save()

        # Log the user in
        auth_login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Clean session
        if 'pre_2fa_user_id' in self.request.session:
            del self.request.session['pre_2fa_user_id']
        self.request.session['admin_otp_verified'] = True

        # Device fingerprint tracking
        ip = self.request.META.get("REMOTE_ADDR", "")
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        device, created = DeviceFingerprint.objects.get_or_create(
            user=user,
            ip_address=ip,
            user_agent=user_agent,
        )
        if created:
            # Alert on unknown device
            try:
                send_mail(
                    subject="[Green Naroda] Security Alert: New Device Login",
                    message=(
                        f"A new device logged into your admin account.\n\n"
                        f"IP: {ip}\nDevice: {user_agent}\n\n"
                        f"If this was not you, contact security immediately."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        else:
            device.save()

        # Audit log
        AdminAuditLog.objects.create(
            user=user,
            action=AdminAuditLog.ActionType.LOGIN,
            details="Successful 2FA OTP Login via admin panel.",
            ip_address=ip,
            user_agent=user_agent,
        )

        return HttpResponseRedirect("/admin/dashboard/")
