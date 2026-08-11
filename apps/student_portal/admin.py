import openpyxl
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import StudentSubmission, StudentCertificate, StudentShowcase

@admin.action(description="Export selected submissions to Excel")
def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="student_submissions.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Submissions"
    
    # Headers
    headers = ["Participation ID", "Student Name", "Parent Name", "Mobile", "School", "Grade", "City", "Competition", "Status", "Date"]
    ws.append(headers)
    
    # Format Headers (Bold)
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
        
    for sub in queryset:
        ws.append([
            sub.participation_id,
            sub.student_name,
            sub.parent_name,
            sub.guardian_mobile,
            sub.school_name,
            sub.grade,
            getattr(sub, 'city', 'Ahmedabad'), # Safely get city
            sub.get_competition_type_display(),
            sub.get_status_display(),
            sub.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    
    # Auto-width
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        ws.column_dimensions[column].width = max_length + 2
        
    wb.save(response)
    return response

@admin.action(description="Approve selected for Showcase")
def approve_for_showcase(modeladmin, request, queryset):
    for sub in queryset:
        sub.status = StudentSubmission.StatusChoices.APPROVED
        sub.save()
        StudentShowcase.objects.get_or_create(submission=sub)

@admin.action(description="Reject selected")
def reject_submissions(modeladmin, request, queryset):
    queryset.update(status=StudentSubmission.StatusChoices.REJECTED)

@admin.register(StudentSubmission)
class StudentSubmissionAdmin(ModelAdmin):
    list_display = ["participation_id", "student_name", "school_name", "grade", "competition_type", "status", "uploaded_work_preview", "created_at"]
    list_filter = ["competition_type", "status", "grade"]
    search_fields = ["student_name", "participation_id", "guardian_mobile", "school_name"]
    readonly_fields = ["participation_id", "created_at", "updated_at", "uploaded_work_preview"]
    actions = [export_to_excel, approve_for_showcase, reject_submissions]

    def uploaded_work_preview(self, obj):
        if obj.uploaded_file:
            if obj.uploaded_file.name.lower().endswith('.pdf'):
                return format_html(
                    '<a href="{}" target="_blank" class="button" style="padding: 5px 10px; background-color: #ef4444; color: white; border-radius: 4px; text-decoration: none;">📄 Download PDF</a>',
                    obj.uploaded_file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank"><img src="{}" style="height: 50px; border-radius: 4px; object-fit: cover;" /></a>',
                    obj.uploaded_file.url, obj.uploaded_file.url
                )
        return "No File"
    uploaded_work_preview.short_description = "Uploaded Work"

@admin.register(StudentCertificate)
class StudentCertificateAdmin(ModelAdmin):
    list_display = ["submission", "issued_at"]
    search_fields = ["submission__student_name", "submission__participation_id"]

@admin.register(StudentShowcase)
class StudentShowcaseAdmin(ModelAdmin):
    list_display = ["submission", "featured", "created_at"]
    list_filter = ["featured"]
    search_fields = ["submission__student_name"]
