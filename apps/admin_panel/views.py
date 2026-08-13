"""
Campaign Admin Panel — Views
============================
Custom Mission Control admin panel. All views restricted to ADMIN/SUPER_ADMIN.
Provides: login, dashboard, pledges, students, organizations, gallery,
events, news, analytics, settings, and Excel exports.
"""
from __future__ import annotations

import csv
import io
import json
import base64
from datetime import timedelta

from django.contrib import messages
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.accounts.models import User, UserRole
from apps.competitions.models import CompetitionRegistration
from apps.events.models import Event
from apps.gallery.models import Photo
from apps.cms.models import LeadershipPhotos
from apps.news.models import NewsArticle

from apps.student_portal.models import StudentSubmission
from apps.volunteers.models import PledgeRegistration


try:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_admin(user) -> bool:
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or getattr(user, "role", None) in (UserRole.ADMIN, UserRole.SUPER_ADMIN)
        )
    )


def _xl_response(filename: str):
    """Return an HttpResponse configured for .xlsx download."""
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


def _style_xl_header(ws, headers: list[str], fill_color: str = "0B5D2A"):
    """Write and style the header row of an Excel sheet."""
    header_fill = PatternFill("solid", fgColor=fill_color)
    header_font = Font(bold=True, color="FFFFFF", size=11)
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col_idx)].width = max(len(header) + 6, 16)
    ws.row_dimensions[1].height = 22


# ─── Mixin ────────────────────────────────────────────────────────────────────

class AdminRequiredMixin:
    """Restrict view to ADMIN and SUPER_ADMIN roles only."""

    def dispatch(self, request, *args, **kwargs):
        if not _is_admin(request.user):
            return redirect("admin_panel:login")
        return super().dispatch(request, *args, **kwargs)


# ─── Login / Logout ───────────────────────────────────────────────────────────

class AdminLoginView(View):
    template_name = "admin_panel/login.html"

    def get(self, request):
        if _is_admin(request.user):
            return redirect("admin_panel:dashboard")
        return render(request, self.template_name)

    def post(self, request):
        from django.http import JsonResponse
        is_ajax = request.POST.get('ajax_upload') == '1'
        
        photos = LeadershipPhotos.objects.first()
        if not photos:
            photos = LeadershipPhotos.objects.create()

        field_map = {
            'president': 'payalben_photo',
            'convener': 'nikunj_photo',
            'kiran_raval': 'kiran_raval_photo',
            'vipul_patel': 'vipul_patel_photo',
            'jayesh_prajapati': 'jayesh_prajapati_photo',
            'chandaben_patel': 'chandaben_patel_photo',
            'divya_khakhi': 'divya_khakhi_photo',
            'nitin_nabin_photo': 'nitin_nabin_photo',
            'bhupendrabhai_patel_photo': 'bhupendrabhai_patel_photo',
            'jagdish_vishwakarma_photo': 'jagdish_vishwakarma_photo',
            'harshbhai_sanghavi_photo': 'harshbhai_sanghavi_photo',
            'ratnakarji_photo': 'ratnakarji_photo',
            'ajay_brahmbhatt_photo': 'ajay_brahmbhatt_photo',
            'anirudhbhai_dave_photo': 'anirudhbhai_dave_photo',
            'prashantbhai_korat_photo': 'prashantbhai_korat_photo',
            'hitendrasinh_chauhan_photo': 'hitendrasinh_chauhan_photo',
            'prerakbhai_shah_photo': 'prerakbhai_shah_photo',
            'hasmukhbhai_patel_photo': 'hasmukhbhai_patel_photo',
            'dineshbhai_makwana_photo': 'dineshbhai_makwana_photo'
        }
        
        updated = False
        
        # Check for standard cropped blob upload
        uploaded = request.FILES.get('photo')
        field_key = request.POST.get('field_key')
        
        if field_key in field_map and uploaded:
            setattr(photos, field_map[field_key], uploaded)
            photos.save()
            if is_ajax:
                url = getattr(photos, field_map[field_key]).url if getattr(photos, field_map[field_key]) else ''
                return JsonResponse({"success": True, "url": url, "message": "Photo uploaded successfully."})
            
            messages.success(request, "Photo uploaded successfully.")
            return redirect('admin_panel:leadership_photos')
            
        # Handle remove logic
        remove_field = request.POST.get("remove_field")
        if remove_field:
            if remove_field in field_map:
                setattr(photos, field_map[remove_field], None)
                updated = True
            elif remove_field in field_map.values():
                setattr(photos, remove_field, None)
                updated = True
                
            if is_ajax and updated:
                photos.save()
                return JsonResponse({"success": True, "message": "Photo removed."})
        
        # Handle regular file uploads (fallback)
        for key, model_field in field_map.items():
            if key in request.FILES:
                setattr(photos, model_field, request.FILES[key])
                updated = True
            elif model_field in request.FILES:
                setattr(photos, model_field, request.FILES[model_field])
                updated = True
                
        if updated:
            photos.save()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Leadership photo updated successfully."})
            messages.success(request, "Leadership photo updated successfully.")

        if is_ajax:
            return JsonResponse({"success": False, "error": "No valid action found."})

        return redirect("admin_panel:leadership_photos")


# ─── News ─────────────────────────────────────────────────────────────────────

class AdminNewsView(AdminRequiredMixin, View):
    template_name = "admin_panel/news.html"

    def get(self, request):
        qs = NewsArticle.objects.select_related("category").order_by("-published_at", "-id")
        q = request.GET.get("q", "").strip()
        status = request.GET.get("status", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))
        if status == "published":
            qs = qs.filter(is_published=True)
        elif status == "draft":
            qs = qs.filter(is_published=False)

        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get("page", 1))

        return render(request, self.template_name, {
            "page_obj": page_obj,
            "total": NewsArticle.objects.count(),
            "published": NewsArticle.objects.filter(is_published=True).count(),
            "q": q, "status": status,
        })


class AdminNewsTogglePublishView(AdminRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(NewsArticle, pk=pk)
        article.is_published = not article.is_published
        if article.is_published and not article.published_at:
            article.published_at = timezone.now()
        article.save(update_fields=["is_published", "published_at"])
        state = "published" if article.is_published else "unpublished"
        messages.success(request, f"Article '{article.title}' {state}.")
        return redirect("admin_panel:news")


# ─── Branding Settings ────────────────────────────────────────────────────────

from apps.cms.models import BrandingSettings

class AdminBrandingHeaderLogosView(AdminRequiredMixin, View):
    template_name = "admin_panel/branding_header_logos.html"

    def get(self, request):
        settings_obj = BrandingSettings.load()
        
        # Determine fallback URLs based on the template
        fallbacks = {
            "my_naroda_logo": "/static/images/logo-mynaroda.jpeg",
            "bjp_logo": "/static/images/logo-bjp.png",
            "pratham_logo": "/static/images/logo-pratham.png",
            "gncn_logo": "/static/images/logo-gncn.png",
        }
        
        return render(request, self.template_name, {
            "branding_settings": settings_obj,
            "fallbacks": fallbacks
        })

    def post(self, request):
        settings_obj = BrandingSettings.load()
        
        try:
            data = json.loads(request.body)
            action = data.get("action")
            field = data.get("field")
            
            valid_fields = ["my_naroda_logo", "bjp_logo", "pratham_logo", "gncn_logo"]
            if field not in valid_fields:
                return JsonResponse({"success": False, "error": "Invalid field"})
            
            if action == "save":
                image_data = data.get("image_data")
                if not image_data:
                    return JsonResponse({"success": False, "error": "No image data provided"})
                
                # Format: data:image/png;base64,iVBORw0KGgo...
                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1] 
                
                # Validate extension
                if ext not in ['png', 'jpg', 'jpeg', 'webp']:
                    ext = 'png'
                
                data_file = ContentFile(base64.b64decode(imgstr), name=f"{field}.{ext}")
                
                # Delete old if exists
                old_file = getattr(settings_obj, field)
                if old_file:
                    old_file.delete(save=False)
                
                setattr(settings_obj, field, data_file)
                settings_obj.save()
                
                # Get the new URL
                new_url = getattr(settings_obj, field).url
                
                return JsonResponse({"success": True, "url": new_url})
                
            elif action == "remove":
                # Delete file
                old_file = getattr(settings_obj, field)
                if old_file:
                    old_file.delete(save=False)
                
                setattr(settings_obj, field, None)
                settings_obj.save()
                return JsonResponse({"success": True})
                
            return JsonResponse({"success": False, "error": "Unknown action"})
            
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


# ─── Har Ghar Tiranga ─────────────────────────────────────────────────────────
from apps.cms.models import HarGharTirangaRegistration

class AdminHarGharTirangaRegistrationsView(AdminRequiredMixin, View):
    template_name = "admin_panel/tiranga_registrations.html"

    def get(self, request):
        qs = HarGharTirangaRegistration.objects.all().order_by("-created_at")
        
        # simple search
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(token_id__icontains=q) |
                Q(name__icontains=q) |
                Q(mobile_number__icontains=q) |
                Q(address__icontains=q)
            )

        paginator = Paginator(qs, 50)
        page_obj = paginator.get_page(request.GET.get("page", 1))
        
        today = timezone.now().date()
        today_count = HarGharTirangaRegistration.objects.filter(created_at__date=today).count()

        return render(request, self.template_name, {
            "page_obj": page_obj,
            "total": qs.count(),
            "today_count": today_count,
            "q": q,
        })


class AdminExportHarGharTirangaExcelView(AdminRequiredMixin, View):
    def get(self, request):
        qs = HarGharTirangaRegistration.objects.all().order_by("-created_at")

        if not HAS_OPENPYXL:
            return HttpResponse("openpyxl not installed.", status=500)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tiranga Registrations"

        headers = [
            "Sr.", "Token ID", "Name", "Mobile Number",
            "Address", "Location", "Registration Date",
        ]
        _style_xl_header(ws, headers)

        for i, reg in enumerate(qs, 1):
            location_str = "Not provided"
            if reg.latitude and reg.longitude:
                location_str = f"{reg.latitude}, {reg.longitude}"
                if reg.location_text:
                    location_str += f" ({reg.location_text})"
                    
            ws.append([
                i,
                reg.token_id or "-",
                reg.name,
                reg.mobile_number,
                reg.address,
                location_str,
                reg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="har_ghar_tiranga_registrations.xlsx"'
        wb.save(response)
        return response


# ─── Organization Types & Associate Organizations ─────────────────────────────
from apps.competitions.models import CompetitionOrganizationType
from apps.volunteers.models import Organization
import json

class AdminOrganizationTypesView(AdminRequiredMixin, View):
    template_name = "admin_panel/org_types.html"

    def get(self, request):
        qs = CompetitionOrganizationType.objects.all().order_by("sort_order", "name")
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return render(request, self.template_name, {"items": qs, "q": q})

    def post(self, request):
        action = request.POST.get("action")
        
        if action == "add":
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            sort_order = request.POST.get("sort_order", 0)
            if not name:
                messages.error(request, "Name cannot be empty.")
            elif CompetitionOrganizationType.objects.filter(name__iexact=name).exists():
                messages.error(request, "Organization type with this name already exists.")
            else:
                try:
                    sort_order = int(sort_order)
                    CompetitionOrganizationType.objects.create(name=name, is_active=is_active, sort_order=sort_order)
                    messages.success(request, "Organization type added.")
                except ValueError:
                    messages.error(request, "Sort order must be numeric.")

        elif action == "edit":
            pk = request.POST.get("id")
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            sort_order = request.POST.get("sort_order", 0)
            
            try:
                obj = CompetitionOrganizationType.objects.get(pk=pk)
                if not name:
                    messages.error(request, "Name cannot be empty.")
                elif CompetitionOrganizationType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
                    messages.error(request, "Organization type with this name already exists.")
                else:
                    obj.name = name
                    obj.is_active = is_active
                    obj.sort_order = int(sort_order)
                    obj.save()
                    messages.success(request, "Organization type updated.")
            except Exception as e:
                messages.error(request, f"Error updating: {e}")

        elif action == "delete":
            pk = request.POST.get("id")
            CompetitionOrganizationType.objects.filter(pk=pk).delete()
            messages.success(request, "Organization type deleted.")
            
        elif action == "toggle":
            pk = request.POST.get("id")
            obj = CompetitionOrganizationType.objects.filter(pk=pk).first()
            if obj:
                obj.is_active = not obj.is_active
                obj.save()
                messages.success(request, f"Organization type {'enabled' if obj.is_active else 'disabled'}.")

        return redirect("admin_panel:org_types")


class AdminAssociateOrganizationsView(AdminRequiredMixin, View):
    template_name = "admin_panel/associate_orgs.html"

    def get(self, request):
        qs = Organization.objects.all().order_by("sort_order", "name")
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return render(request, self.template_name, {"items": qs, "q": q})

    def post(self, request):
        action = request.POST.get("action")
        
        if action == "add":
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            sort_order = request.POST.get("sort_order", 0)
            if not name:
                messages.error(request, "Name cannot be empty.")
            elif Organization.objects.filter(name__iexact=name).exists():
                messages.error(request, "Organization with this name already exists.")
            else:
                try:
                    sort_order = int(sort_order)
                    Organization.objects.create(name=name, is_active=is_active, sort_order=sort_order)
                    messages.success(request, "Associate organization added.")
                except ValueError:
                    messages.error(request, "Sort order must be numeric.")

        elif action == "edit":
            pk = request.POST.get("id")
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            sort_order = request.POST.get("sort_order", 0)
            
            try:
                obj = Organization.objects.get(pk=pk)
                if not name:
                    messages.error(request, "Name cannot be empty.")
                elif Organization.objects.filter(name__iexact=name).exclude(pk=pk).exists():
                    messages.error(request, "Organization with this name already exists.")
                else:
                    obj.name = name
                    obj.is_active = is_active
                    obj.sort_order = int(sort_order)
                    obj.save()
                    messages.success(request, "Associate organization updated.")
            except Exception as e:
                messages.error(request, f"Error updating: {e}")

        elif action == "delete":
            pk = request.POST.get("id")
            Organization.objects.filter(pk=pk).delete()
            messages.success(request, "Associate organization deleted.")
            
        elif action == "toggle":
            pk = request.POST.get("id")
            obj = Organization.objects.filter(pk=pk).first()
            if obj:
                obj.is_active = not obj.is_active
                obj.save()
                messages.success(request, f"Associate organization {'enabled' if obj.is_active else 'disabled'}.")

        return redirect("admin_panel:associate_orgs")

