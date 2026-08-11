from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import CompetitionRegistration
from .utils import generate_organization_certificate

class CompetitionRegistrationView(View):
    template_name = "competitions/registration_form.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            # Extract basic fields
            org_type_id = request.POST.get("organization_type")
            org_name = request.POST.get("organization_name")
            reg_num = request.POST.get("registration_number", "")
            address = request.POST.get("address")
            city = request.POST.get("city")
            pincode = request.POST.get("pincode")

            # Extract conditionally
            homes_count = request.POST.get("homes_count")
            members_participating = request.POST.get("members_participating")

            if homes_count:
                homes_count = int(homes_count)
            else:
                homes_count = None
                
            if members_participating:
                members_participating = int(members_participating)
            else:
                members_participating = None

            # Extract contact fields
            contact_name = request.POST.get("authorized_person_name")
            designation = request.POST.get("designation", "")
            mobile = request.POST.get("mobile_number")
            whatsapp = request.POST.get("whatsapp_number")
            alternate = request.POST.get("alternate_number", "")
            email = request.POST.get("email")

            # Extract sustainability fields
            solar_installed = request.POST.get("solar_installed") == "yes"
            solar_count = request.POST.get("solar_panels_count")
            if solar_count:
                solar_count = int(solar_count)
            else:
                solar_count = None

            rainwater = request.POST.get("rainwater_harvesting") == "yes"

            # Extract file
            supporting_file = request.FILES.get("supporting_file")

            from .models import CompetitionOrganizationType
            try:
                org_type_instance = CompetitionOrganizationType.objects.get(id=org_type_id)
            except CompetitionOrganizationType.DoesNotExist:
                return JsonResponse({"success": False, "message": "Invalid organization type."}, status=400)

            # Validate basic required fields
            if not all([org_type_id, org_name, address, city, pincode, contact_name, mobile, whatsapp, email]):
                return JsonResponse({"success": False, "message": "Please fill all required fields."}, status=400)

            if "society" in org_type_instance.name.lower() and not homes_count:
                 return JsonResponse({"success": False, "message": "Number of homes is required for societies."}, status=400)
                 
            # Create object
            registration = CompetitionRegistration(
                organization_type=org_type_instance,
                organization_name=org_name,
                registration_number=reg_num,
                address=address,
                city=city,
                pincode=pincode,
                homes_count=homes_count,
                members_participating=members_participating,
                authorized_person_name=contact_name,
                designation=designation,
                mobile_number=mobile,
                whatsapp_number=whatsapp,
                alternate_number=alternate,
                email=email,
                solar_installed=solar_installed,
                solar_panels_count=solar_count,
                rainwater_harvesting=rainwater,
                supporting_file=supporting_file
            )
            
            registration.save()
            
            # Generate Certificates (PNG & PDF)
            generate_organization_certificate(registration)
            
            return JsonResponse({
                "success": True, 
                "message": "Registration submitted successfully.",
                "registration_id": registration.registration_id
            })
            
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

class VerifyOrganizationCertificateView(View):
    template_name = "competitions/verify_certificate.html"

    def get(self, request, registration_id):
        # Look up by exact registration_id
        registration = get_object_or_404(CompetitionRegistration, registration_id=registration_id)
        
        context = {
            "registration": registration,
            "is_valid": registration.certificate_generated and registration.status != CompetitionRegistration.ApprovalStatus.REJECTED
        }
        return render(request, self.template_name, context)

