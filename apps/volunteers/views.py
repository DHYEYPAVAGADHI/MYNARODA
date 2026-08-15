import json
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
import html

from apps.accounts.models import User, UserRole
from apps.volunteers.models import PledgeRegistration, Organization
from apps.volunteers.tasks import generate_certificate_task
from apps.volunteers.utils import generate_certificate_id, generate_tree_number, assign_freedom_fighter_name

class VolunteerLeaderboardView(View):
    template_name = "volunteers/leaderboard.html"

    def get(self, request):
        volunteers = User.objects.filter(
            role=UserRole.VOLUNTEER, 
            is_active=True
        ).order_by("-trees_planted", "-total_hours")[:20]

        context = {
            "volunteers": volunteers,
        }
        return render(request, self.template_name, context)

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=False), name='post')
class SubmitPledgeRegistrationView(View):
    def post(self, request, *args, **kwargs):
        was_limited = getattr(request, 'limited', False)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
        
        if was_limited:
            if is_ajax:
                return JsonResponse({"status": "error", "message": "Too many requests. Please try again later."}, status=429)
            messages.error(request, _("Too many requests. Please try again later."))
            return redirect("cms:home")
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        full_name = html.escape(data.get("full_name", "").strip())
        mobile_number = data.get("mobile_number")
        email = data.get("email", "")
        dob_str = data.get("date_of_birth")
        gender = data.get("gender")

        org_id = data.get("organization")

        pledge_consent = data.get("pledge_consent") in ["on", True, "true", "1", True]

        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip

        ip_address = get_client_ip(request)
        browser_info = request.META.get('HTTP_USER_AGENT', '')[:255]

        try:
            # Validate required checkbox
            if not pledge_consent:
                raise ValueError(_("You must accept the official pledge and consent to proceed."))
                
            if not dob_str:
                raise ValueError(_("Date of birth is required."))

            date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()

            if not org_id:
                raise ValueError(_("You must select an Associate Organization."))
            org = Organization.objects.filter(id=org_id).first()
            if not org:
                raise ValueError(_("Invalid Associate Organization selected."))

            # Create approved pledge directly
            pledge = PledgeRegistration.objects.create(
                full_name=full_name,
                mobile_number=mobile_number,
                email=email.lower() if email else "",
                date_of_birth=date_of_birth,
                gender=gender,
                organization=org,
                agreed_to_pledge=True,
                consent_accepted=True,
                ip_address=ip_address,
                browser_info=browser_info,
                otp_verified=True,
                is_approved=True
            )
            
            pledge.certificate_id = generate_certificate_id()
            pledge.tree_number = generate_tree_number()
            tree_sequence = int(pledge.tree_number.rsplit("/", 1)[-1])
            pledge.dedicated_to = assign_freedom_fighter_name(tree_sequence)
            pledge.save(update_fields=['certificate_id', 'tree_number', 'dedicated_to'])
            
            # Trigger certificate generation synchronously so we can return the URLs
            # The generation task itself will asynchronously trigger whatsapp and email tasks
            generate_certificate_task(pledge.id)
            
            # Fetch the updated pledge to get the certificate URLs
            pledge.refresh_from_db()
            
            if is_ajax:
                from django.utils import timezone
                submission_date = timezone.localtime(pledge.created_at).strftime("%d %B %Y") if pledge.created_at else ""
                return JsonResponse({
                    "status": "success",
                    "pledge_id": pledge.id,
                    "full_name": pledge.full_name,
                    "certificate_id": pledge.certificate_id,
                    "tree_number": pledge.tree_number,
                    "tree_name": pledge.dedicated_to.name if pledge.dedicated_to else "",
                    "plantation_location": "Naroda",
                    "submission_date": submission_date,
                    "certificate_image_url": pledge.certificate_image.url if pledge.certificate_image else None,
                    "certificate_pdf_url": pledge.certificate_pdf.url if pledge.certificate_pdf else None,
                    "citizens_joined": PledgeRegistration.objects.filter(is_approved=True).count()
                })
            
            messages.success(request, _("Pledge submitted successfully!"))
            return redirect("cms:home")
            
        except Exception as e:
            if is_ajax:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
            messages.error(request, _("An error occurred. Please try again."))
            return redirect("cms:home")

class TrackShareView(View):
    def post(self, request, *args, **kwargs):
        import json
        from django.shortcuts import get_object_or_404
        try:
            data = json.loads(request.body)
            pledge_id = data.get('pledge_id')
            action = data.get('action')
            
            pledge = get_object_or_404(PledgeRegistration, id=pledge_id)
            
            if action == 'download':
                pledge.download_count += 1
            elif action == 'ig':
                pledge.share_ig_count += 1
            elif action == 'wa':
                pledge.share_wa_count += 1
            elif action == 'fb':
                pledge.share_fb_count += 1
                
            pledge.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

class VerifyCertificateView(View):
    def get(self, request, certificate_id):
        pledge = get_object_or_404(PledgeRegistration, certificate_id=certificate_id)
        return render(request, "certificates/verify.html", {"pledge": pledge})
