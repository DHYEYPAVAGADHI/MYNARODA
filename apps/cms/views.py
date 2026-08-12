import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.cms.models import Partner, SiteSettings, Testimonial, ContactMessage, PageMission, LeadershipPhotos
from apps.events.models import Event
from apps.gallery.models import Photo
from apps.trees.models import Tree, TreeSpecies
from apps.accounts.models import User, UserRole

from core.utils import calculate_campaign_progress, days_until_independence_day


class LandingPageView(View):
    """Class-based view for the campaign landing page."""
    template_name = "pages/landing.html"

    def get(self, request):
        site_settings = SiteSettings.objects.first()
        if not site_settings:
            # Create a default settings object if none exists
            site_settings = SiteSettings.objects.create(
                trees_planted=1247,
                volunteers_count=352,
                events_count=12,
                photos_count=45
            )

        # ── Live Activity Feed ────────────────────────────────────────────────
        activities = []
        
        # User signups (Volunteers and Citizens)
        recent_users = User.objects.filter(is_active=True).order_by("-created_at")[:5]
        for u in recent_users:
            role_label = _("volunteer") if u.role == UserRole.VOLUNTEER else _("citizen")
            activities.append({
                "time": u.created_at,
                "text": _("New {role} {name} joined the movement.").format(role=role_label, name=u.full_name or u.email.split("@")[0]),
                "icon": "👤"
            })
            
        # Trees planted
        recent_trees = Tree.objects.select_related("species", "planted_by").order_by("-created_at")[:5]
        for t in recent_trees:
            planter = t.planted_by.full_name if t.planted_by else (_("A citizen") if t.contributor else _("Anonymous"))
            activities.append({
                "time": t.created_at,
                "text": _("{planter} planted a {species} tree in Ward {ward}.").format(planter=planter, species=t.species.name, ward=t.ward or _("Naroda")),
                "icon": "🌳"
            })

        # Gallery uploads
        recent_photos = Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED).select_related("photographer").order_by("-approved_at")[:5]
        for p in recent_photos:
            photog = p.photographer.full_name if p.photographer else _("Anonymous")
            activities.append({
                "time": p.approved_at or p.created_at,
                "text": _("New photograph approved from photographer {photographer}.").format(photographer=photog),
                "icon": "📸"
            })

        # Sort activities by time descending
        activities.sort(key=lambda x: x["time"] or timezone.now(), reverse=True)
        activities = activities[:10]

        # ── Live Campaign Status (Today/This Week/Total/Active) ──────────────
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - datetime.timedelta(days=7)

        trees_today = Tree.objects.filter(created_at__gte=today_start).count()
        trees_this_week = Tree.objects.filter(created_at__gte=week_start).count()
        total_trees = Tree.objects.count()
        today_volunteers = User.objects.filter(role=UserRole.VOLUNTEER, created_at__gte=today_start).count()
        active_events = Event.objects.filter(status=Event.EventStatus.ONGOING).count()
        pending_approvals = Photo.objects.filter(approval_status=Photo.ApprovalStatus.PENDING).count()

        # Update SiteSettings dynamic numbers on landing page load to keep it updated
        site_settings.trees_planted = total_trees
        site_settings.volunteers_count = User.objects.filter(role=UserRole.VOLUNTEER).count()
        site_settings.events_count = Event.objects.count()
        site_settings.photos_count = Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED).count()
        site_settings.save()

        # ── Environmental Impact stats ────────────────────────────────────────
        est_oxygen = total_trees * 120
        est_carbon = total_trees * 22
        est_water = total_trees * 1000

        # Calculate progress
        progress_pct = calculate_campaign_progress(total_trees)
        
        # Load Homepage and its active slides
        from apps.cms.models import Homepage
        homepage = Homepage.load()
        hero_slides = homepage.hero_slides.filter(is_active=True).order_by("sort_order")
        
        # Load Student Corner Showcases
        try:
            from apps.student_corner.models import StudentShowcase
            showcases = StudentShowcase.objects.filter(featured=True).select_related("submission")
        except ImportError:
            showcases = []


        from apps.competitions.models import CompetitionRegistration

        total_orgs = CompetitionRegistration.objects.count()
        # Load approved gallery photos for homepage
        gallery_photos = Photo.objects.filter(
            approval_status=Photo.ApprovalStatus.APPROVED
        ).order_by("-created_at")[:12]
        # Load latest 3 published news articles
        from apps.news.models import NewsArticle
        news_articles = NewsArticle.objects.filter(is_published=True).order_by("-published_at")[:3]

        context = {
            "site_settings": site_settings,
            "showcases": showcases,
            "hero_slides": hero_slides,
            "featured_photos": Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED, is_featured=True).order_by("-created_at")[:8],
            "gallery_photos": gallery_photos,
            "leadership_photos": LeadershipPhotos.objects.first(),
            "news_articles": news_articles,

            "upcoming_events": Event.objects.filter(is_published=True, starts_at__gte=timezone.now()).order_by("starts_at")[:4],
            "testimonials": Testimonial.objects.filter(is_active=True).order_by("sort_order")[:8],
            "partners": Partner.objects.filter(is_active=True).order_by("sort_order"),

            "progress_pct": progress_pct,
            "days_remaining": days_until_independence_day(2027),
            "activities": activities,
            "trees_today": trees_today,
            "trees_this_week": trees_this_week,
            "today_volunteers": today_volunteers,
            "active_events": active_events,
            "pending_approvals": pending_approvals,
            "est_oxygen": est_oxygen,
            "est_carbon": est_carbon,
            "est_water": est_water,
            "total_trees": total_trees,
            "total_orgs": total_orgs,
            "cloudinary_cloud_name": getattr(settings, "CLOUDINARY_STORAGE", {}).get("CLOUD_NAME", ""),
        }
        return render(request, self.template_name, context)


class AboutPageView(View):
    """View rendering the mission, vision, and team details."""
    template_name = "pages/about.html"

    def get(self, request):
        return render(request, self.template_name, {
            "days_remaining": days_until_independence_day(2027),
            "total_trees": Tree.objects.count(),
            "total_volunteers": User.objects.filter(role=UserRole.VOLUNTEER).count(),
        })


class ContactPageView(View):
    """View managing the contact form submissions."""
    template_name = "pages/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not name or not email or not subject or not message:
            messages.error(request, _("All fields are required. Please try again."))
            return render(request, self.template_name)

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Send an email notification to the Nodal Office
        from django.core.mail import send_mail
        try:
            send_mail(
                subject=f"New Contact Message: {subject}",
                message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email="noreply@mynaroda.in",
                recipient_list=["prathampriority@mynaroda.in"],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, _("Thank you for reaching out! Your message has been sent successfully."))
        return redirect("cms:contact")


class ImpactPageView(View):
    """Dedicated environmental impact dashboard."""
    template_name = "pages/impact.html"

    def get(self, request):
        import json
        from collections import defaultdict
        
        # Import dynamically if not at top of file
        from apps.volunteers.models import PledgeRegistration

        total_trees = Tree.objects.count()
        est_oxygen = total_trees * 120
        est_carbon = total_trees * 22
        est_water = total_trees * 1000
        shade_area = total_trees * 15
        temp_reduction = 1.5 if total_trees > 5000 else 0.5

        all_trees = list(Tree.objects.all())
        all_pledges = list(PledgeRegistration.objects.all())

        # 1. Ward-wise Distribution
        ward_distribution = {}
        for t in all_trees:
            ward_name = t.ward or _("Other / Naroda")
            ward_distribution[ward_name] = ward_distribution.get(ward_name, 0) + 1

        ward_stats = sorted(
            [{"ward": str(k), "count": v} for k, v in ward_distribution.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        # Format for Chart.js Ward Donut
        chart_ward_labels = [item["ward"] for item in ward_stats]
        chart_ward_data = [item["count"] for item in ward_stats]

        # 2. Campaign Growth (Last 7 Days)
        now = timezone.now()
        dates = [(now - datetime.timedelta(days=i)).date() for i in range(6, -1, -1)]
        date_str_list = [d.strftime("%b %d") for d in dates]
        
        daily_pledges = {d: 0 for d in dates}
        for p in all_pledges:
            d = p.created_at.date()
            if d in daily_pledges:
                daily_pledges[d] += 1
                
        daily_trees = {d: 0 for d in dates}
        for t in all_trees:
            d = t.created_at.date()
            if d in daily_trees:
                daily_trees[d] += 1

        chart_dates = date_str_list
        chart_pledges = [daily_pledges[d] for d in dates]
        chart_trees = [daily_trees[d] for d in dates]

        # 3. Gender Demographics
        gender_dist = {"Male": 0, "Female": 0, "Other": 0}
        for p in all_pledges:
            g = p.gender.upper() if p.gender else ""
            if g == "MALE" or g == "M": gender_dist["Male"] += 1
            elif g == "FEMALE" or g == "F": gender_dist["Female"] += 1
            else: gender_dist["Other"] += 1
            
        chart_gender_labels = list(gender_dist.keys())
        chart_gender_data = list(gender_dist.values())

        # 4. Age Groups
        age_dist = {"< 18": 0, "18-25": 0, "26-40": 0, "41-60": 0, "60+": 0, "Unknown": 0}
        for p in all_pledges:
            if p.age is None:
                if not p.date_of_birth:
                    age_dist["Unknown"] += 1
                    continue
                age = (now.date() - p.date_of_birth).days / 365.25
            else:
                age = p.age

            if age < 18: age_dist["< 18"] += 1
            elif age <= 25: age_dist["18-25"] += 1
            elif age <= 40: age_dist["26-40"] += 1
            elif age <= 60: age_dist["41-60"] += 1
            else: age_dist["60+"] += 1
            
        chart_age_labels = list(age_dist.keys())
        chart_age_data = list(age_dist.values())

        context = {
            "total_trees": total_trees,
            "est_oxygen": est_oxygen,
            "est_carbon": est_carbon,
            "est_water": est_water,
            "shade_area": shade_area,
            "temp_reduction": temp_reduction,
            "ward_stats": ward_stats,
            # JSON Data for Charts
            "chart_ward_labels": json.dumps(chart_ward_labels),
            "chart_ward_data": json.dumps(chart_ward_data),
            "chart_dates": json.dumps(chart_dates),
            "chart_pledges": json.dumps(chart_pledges),
            "chart_trees": json.dumps(chart_trees),
            "chart_gender_labels": json.dumps(chart_gender_labels),
            "chart_gender_data": json.dumps(chart_gender_data),
            "chart_age_labels": json.dumps(chart_age_labels),
            "chart_age_data": json.dumps(chart_age_data),
        }
        return render(request, self.template_name, context)



class PrivacyPageView(View):
    """View for privacy policy."""
    template_name = "pages/privacy.html"

    def get(self, request):
        return render(request, self.template_name)


class TermsPageView(View):
    """View for terms of use."""
    template_name = "pages/terms.html"

    def get(self, request):
        return render(request, self.template_name)


class GreenNarodaPageView(View):
    """View for the Green Naroda mission page."""
    template_name = "pages/green_naroda.html"

    def get(self, request):
        page = PageMission.objects.filter(slug="green-naroda").prefetch_related(
            "objectives", "highlights", "activities", "statistics", "timelines"
        ).first()
        
        context = {
            "page": page,
            "days_remaining": days_until_independence_day(2027),

            "featured_photos": Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED, is_featured=True).order_by("-created_at")[:6],

        }
        return render(request, self.template_name, context)


class CleanNarodaPageView(View):
    """View for the Clean Naroda mission page."""
    template_name = "pages/clean_naroda.html"

    def get(self, request):
        page = PageMission.objects.filter(slug="clean-naroda").prefetch_related(
            "objectives", "highlights", "activities", "statistics", "timelines"
        ).first()
        
        context = {
            "page": page,
            "days_remaining": days_until_independence_day(2027),

            "featured_photos": Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED, is_featured=True).order_by("-created_at")[:6],

        }
        return render(request, self.template_name, context)

import json
from django.http import JsonResponse
from apps.cms.models import HarGharTirangaRegistration

class HarGharTirangaRegistrationView(View):
    """View for Har Ghar Tiranga Registration."""
    template_name = "pages/har_ghar_tiranga_registration.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            name = request.POST.get("name", "").strip()
            mobile_number = request.POST.get("mobile_number", "").strip()
            address = request.POST.get("address", "").strip()
            
            # Safely handle latitude and longitude
            lat_str = request.POST.get("latitude", "").strip()
            lon_str = request.POST.get("longitude", "").strip()
            latitude = float(lat_str) if lat_str and lat_str not in ["undefined", "null"] else None
            longitude = float(lon_str) if lon_str and lon_str not in ["undefined", "null"] else None
            
            location_text = request.POST.get("location_text", "")

            # Validation
            if len(name) < 3:
                msg = "Name must be at least 3 characters long."
                return JsonResponse({"success": False, "error": msg, "message": msg})
            if len(mobile_number) != 10 or not mobile_number.isdigit():
                msg = "Mobile number must be exactly 10 digits."
                return JsonResponse({"success": False, "error": msg, "message": msg})
            if len(address) < 10:
                msg = "Address must be at least 10 characters long."
                return JsonResponse({"success": False, "error": msg, "message": msg})

            # Save to DB
            registration = HarGharTirangaRegistration.objects.create(
                name=name,
                mobile_number=mobile_number,
                address=address,
                latitude=latitude,
                longitude=longitude,
                location_text=location_text
            )

            # Generate Unique Token
            token_id = f"HGT-NRD-2026-{registration.id:05d}"
            registration.token_id = token_id
            registration.save(update_fields=['token_id'])

            return JsonResponse({"success": True, "token_id": token_id, "message": "Registration successful."})
        except Exception as e:
            error_msg = str(e) or "Unknown server error occurred."
            return JsonResponse({"success": False, "error": error_msg, "message": error_msg})
