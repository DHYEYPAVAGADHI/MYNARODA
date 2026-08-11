from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CompetitionRegistration

@method_decorator(csrf_exempt, name='dispatch')
class OrganizationCertificateLookupView(View):
    def post(self, request):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                reg_id = data.get("registration_id")
                mobile = data.get("mobile")
            else:
                reg_id = request.POST.get("registration_id")
                mobile = request.POST.get("mobile")

            if not reg_id or not mobile:
                return JsonResponse({"success": False, "message": "Missing registration_id or mobile."})

            # Check if exists
            try:
                org = CompetitionRegistration.objects.get(
                    registration_id=reg_id,
                    mobile_number=mobile
                )
            except CompetitionRegistration.DoesNotExist:
                return JsonResponse({
                    "success": False, 
                    "message": "Certificate not found. Please check your Registration ID and mobile number."
                })

            # If not generated, just in case (though it should be auto-generated)
            if not org.certificate_generated or not org.certificate_png or not org.certificate_pdf:
                from .utils import generate_organization_certificate
                generate_organization_certificate(org)
                # Re-fetch
                org.refresh_from_db()

            return JsonResponse({
                "success": True,
                "organization_name": org.organization_name,
                "certificate_png": org.certificate_png.url if org.certificate_png else None,
                "certificate_pdf": org.certificate_pdf.url if org.certificate_pdf else None,
            })
            
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
