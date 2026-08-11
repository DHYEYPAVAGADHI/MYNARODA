import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

def admin_otp_verify(request):
    """
    View for verifying OTP to access the Django Admin.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/admin/login/')

    if request.session.get('admin_otp_verified', False):
        return redirect('/admin/')

    # Generate OTP if not present or expired (simple approach)
    if 'admin_otp' not in request.session:
        otp = str(random.randint(100000, 999999))
        request.session['admin_otp'] = otp
        request.session['admin_otp_expiry'] = (timezone.now() + timedelta(minutes=10)).timestamp()
        
        # During development print OTP in terminal, in production send by email
        print(f"\n======================================")
        print(f"ADMIN LOGIN OTP FOR {request.user.email}: {otp}")
        print(f"======================================\n")

    if request.method == "POST":
        if "resend" in request.POST:
            del request.session['admin_otp']
            messages.success(request, "New OTP generated and sent.")
            return redirect('admin_otp_verify')

        entered_otp = request.POST.get('otp', '').strip()
        expiry = request.session.get('admin_otp_expiry', 0)
        
        if timezone.now().timestamp() > expiry:
            messages.error(request, "OTP has expired. Please request a new one.")
            if 'admin_otp' in request.session:
                del request.session['admin_otp']
        elif entered_otp == request.session.get('admin_otp'):
            request.session['admin_otp_verified'] = True
            messages.success(request, "Admin access granted.")
            return redirect('/admin/')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "admin/otp_verify.html")
