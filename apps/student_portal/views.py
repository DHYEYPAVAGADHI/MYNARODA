import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import StudentSubmission, StudentShowcase
from .utils import generate_certificate

def portal_home(request):
    return render(request, "student_portal/home.html")

def showcase(request):
    showcases = StudentShowcase.objects.filter(featured=True).select_related("submission")
    return render(request, "student_portal/showcase.html", {"showcases": showcases})

def essay_form(request):
    context = {
        "category_value": StudentSubmission.CompetitionType.ESSAY,
        "category_name": "Essay Writing Competition",
    }
    return render(request, "student_portal/form.html", context)

def drawing_form(request):
    context = {
        "category_value": StudentSubmission.CompetitionType.DRAWING,
        "category_name": "Drawing Competition",
    }
    return render(request, "student_portal/form.html", context)

def project_form(request):
    context = {
        "category_value": StudentSubmission.CompetitionType.SUSTAINABLE_PROJECT,
        "category_name": "Sustainable Project Making",
    }
    return render(request, "student_portal/form.html", context)

@csrf_exempt
def api_check_mobile(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        if not mobile:
            return JsonResponse({"error": "No mobile number provided"}, status=400)
            
        exists = StudentSubmission.objects.filter(guardian_mobile=mobile).exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def api_submit(request):
    if request.method == "POST":
        try:
            # Extract basic fields
            competition_type = request.POST.get('competition_type')
            student_name = request.POST.get('student_name')
            parent_name = request.POST.get('parent_name')
            guardian_mobile = request.POST.get('guardian_mobile')
            school_name = request.POST.get('school_name')
            city = request.POST.get('city', 'Ahmedabad') # The prompt mentioned city
            grade = request.POST.get('grade')
            consent = request.POST.get('consent') == 'true'
            
            # Extract files
            uploaded_file = request.FILES.get('uploaded_file')
            student_photo = request.FILES.get('student_photo')

            # Basic Validation
            if not uploaded_file:
                return JsonResponse({"status": "error", "message": "No file uploaded"}, status=400)
                
            if not all([competition_type, student_name, parent_name, guardian_mobile, school_name, grade, consent]):
                return JsonResponse({"error": "All required fields must be provided."}, status=400)
                
            if len(guardian_mobile) != 10 or not guardian_mobile.isdigit():
                return JsonResponse({"error": "Invalid mobile number. Must be 10 digits."}, status=400)
                
            # Double check duplicate
            if StudentSubmission.objects.filter(guardian_mobile=guardian_mobile).exists():
                return JsonResponse({
                    "error": "Participation already registered for this mobile number."
                }, status=400)
                
            try:
                grade = int(grade)
                if not (1 <= grade <= 8):
                    raise ValueError
            except ValueError:
                return JsonResponse({"error": "Grade must be between 1 and 8."}, status=400)
                
            # Create Submission
            try:
                submission = StudentSubmission.objects.create(
                    competition_type=competition_type,
                    student_name=student_name,
                    parent_name=parent_name,
                    guardian_mobile=guardian_mobile,
                    school_name=school_name,
                    grade=grade,
                    uploaded_file=uploaded_file,
                    student_photo=student_photo,
                    consent=consent,
                )
            except IntegrityError:
                return JsonResponse({
                    "error": "Participation already registered. This mobile number has already been used for a Student Portal competition. Each student can participate only once."
                }, status=400)
            
            # Generate Certificate
            cert = generate_certificate(submission)
            
            return JsonResponse({
                "message": "Participation Submitted Successfully!",
                "participation_id": submission.participation_id,
                "certificate_png": cert.certificate_png.url if cert.certificate_png else "",
                "certificate_pdf": cert.certificate_pdf.url if cert.certificate_pdf else "",
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)
