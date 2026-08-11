"""
CMS App — Enhanced Admin Dashboard Views
==========================================
Powers the premium command-center dashboard with live KPIs,
chart data, and activity feeds.
"""

import datetime
import json
from django.utils import timezone
from django.utils.timesince import timesince
from django.db.models import Count, Q
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth.mixins import UserPassesTestMixin
import os
from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse
import io
import zipfile

from apps.volunteers.models import PledgeRegistration
from apps.trees.models import Tree
from apps.gallery.models import Photo
from apps.certificates.models import Certificate
from apps.accounts.models import User, UserRole


class CustomDashboardView(UserPassesTestMixin, TemplateView):
    title = "Command Center"
    template_name = "admin/custom_dashboard.html"
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        context['title'] = self.title

        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - datetime.timedelta(days=7)

        # ── Core KPIs ─────────────────────────────────────────────
        total_pledges = PledgeRegistration.objects.count()
        today_pledges = PledgeRegistration.objects.filter(created_at__gte=today).count()
        pending_photos = Photo.objects.filter(approval_status=Photo.ApprovalStatus.PENDING).count()
        approved_photos = Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED).count()
        certificates_total = Certificate.objects.count()

        # Competition stats
        from apps.competitions.models import CompetitionRegistration
        comp_total = CompetitionRegistration.objects.count()
        comp_pending = CompetitionRegistration.objects.filter(status=CompetitionRegistration.ApprovalStatus.PENDING).count()
        comp_approved = CompetitionRegistration.objects.filter(status=CompetitionRegistration.ApprovalStatus.APPROVED).count()
        comp_by_type = CompetitionRegistration.objects.values('organization_type').annotate(count=Count('id'))
        comp_type_labels = []
        comp_type_data = []
        type_display = dict(CompetitionRegistration.OrganizationType.choices)
        for item in comp_by_type:
            comp_type_labels.append(type_display.get(item['organization_type'], item['organization_type']))
            comp_type_data.append(item['count'])

        # News & Events
        try:
            from apps.news.models import NewsArticle
            news_published = NewsArticle.objects.filter(is_published=True).count()
        except Exception:
            news_published = 0

        try:
            from apps.events.models import Event
            events_published = Event.objects.filter(is_published=True).count()
            upcoming_events = Event.objects.filter(
                is_published=True, starts_at__gte=now
            ).order_by('starts_at')[:3]
        except Exception:
            events_published = 0
            upcoming_events = []

        try:
            from apps.cms.models import FAQ
            faq_count = FAQ.objects.filter(is_active=True).count()
        except Exception:
            faq_count = 0

        # ── Chart 1: Daily pledges — last 14 days ─────────────────
        chart_dates = []
        chart_pledge_counts = []
        for i in range(13, -1, -1):
            day = today - datetime.timedelta(days=i)
            next_day = day + datetime.timedelta(days=1)
            count = PledgeRegistration.objects.filter(
                created_at__gte=day, created_at__lt=next_day
            ).count()
            chart_dates.append(day.strftime("%d %b"))
            chart_pledge_counts.append(count)

        # ── Chart 2: Photo approvals — pending/approved/rejected ──
        photo_pending_count = Photo.objects.filter(approval_status=Photo.ApprovalStatus.PENDING).count()
        photo_approved_count = Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED).count()
        photo_rejected_count = Photo.objects.filter(approval_status=Photo.ApprovalStatus.REJECTED).count()

        # ── Activity Feed ─────────────────────────────────────────
        activity = []

        for p in PledgeRegistration.objects.order_by('-created_at')[:4]:
            activity.append({
                'type': 'pledge',
                'icon': '🌱',
                'color': 'green',
                'text': f"<strong>{p.full_name}</strong> took the pledge",
                'time': timesince(p.created_at) + ' ago',
                'ts': p.created_at,
            })

        for c in CompetitionRegistration.objects.order_by('-created_at')[:3]:
            activity.append({
                'type': 'competition',
                'icon': '🏢',
                'color': 'saffron',
                'text': f"<strong>{c.organization_name}</strong> registered for competition",
                'time': timesince(c.created_at) + ' ago',
                'ts': c.created_at,
            })

        for ph in Photo.objects.order_by('-created_at')[:3]:
            activity.append({
                'type': 'photo',
                'icon': '📸',
                'color': 'blue',
                'text': f"New photo uploaded: <strong>{ph.title or 'Untitled'}</strong>",
                'time': timesince(ph.created_at) + ' ago',
                'ts': ph.created_at,
            })

        # Sort by timestamp desc and take top 8
        activity.sort(key=lambda x: x['ts'], reverse=True)
        activity = activity[:8]

        # ── Recent Pledges table ───────────────────────────────────
        recent_pledges = PledgeRegistration.objects.order_by('-created_at').select_related('organization')[:8]

        context.update({
            # KPIs
            'total_pledges': total_pledges,
            'today_pledges': today_pledges,
            'pending_photos': pending_photos,
            'approved_photos': approved_photos,
            'certificates_total': certificates_total,
            'comp_total': comp_total,
            'comp_pending': comp_pending,
            'comp_approved': comp_approved,
            'news_published': news_published,
            'events_published': events_published,
            'faq_count': faq_count,

            # Table data
            'recent_pledges': recent_pledges,
            'upcoming_events': upcoming_events,

            # Activity
            'activity_feed': activity,

            # Charts JSON
            'chart_dates_json': json.dumps(chart_dates),
            'chart_pledge_counts_json': json.dumps(chart_pledge_counts),
            'chart_photo_labels_json': json.dumps(['Pending', 'Approved', 'Rejected']),
            'chart_photo_data_json': json.dumps([photo_pending_count, photo_approved_count, photo_rejected_count]),
            'chart_comp_labels_json': json.dumps(comp_type_labels if comp_type_labels else ['Schools', 'Colleges', 'Societies', 'NGOs']),
            'chart_comp_data_json': json.dumps(comp_type_data if comp_type_data else [0, 0, 0, 0]),

            # Admin user
            'admin_user': self.request.user,
        })

        return context


class BackupAdminView(UserPassesTestMixin, TemplateView):
    template_name = "admin/backup.html"
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        context['title'] = "System Backup"
        return context

    def post(self, request, *args, **kwargs):
        out = io.StringIO()
        call_command("dumpdata", stdout=out, exclude=["contenttypes", "auth.Permission"])

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("database_backup.json", out.getvalue())

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        filename = f"mynaroda_backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        from apps.accounts.models import AdminAuditLog
        AdminAuditLog.objects.create(
            user=request.user,
            action=AdminAuditLog.ActionType.UPDATE,
            details="Generated and downloaded system backup.",
            ip_address=request.META.get("REMOTE_ADDR")
        )

        return response
