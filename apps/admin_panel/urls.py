"""Admin Panel App — URL Configuration"""
from django.urls import path
from apps.admin_panel import views

app_name = "admin_panel"

urlpatterns = [
    # Auth
    path("login/", views.AdminLoginView.as_view(), name="login"),
    path("logout/", views.AdminLogoutView.as_view(), name="logout"),

    # Main panels
    path("", views.AdminDashboardView.as_view(), name="dashboard"),
    path("dashboard/", views.AdminDashboardView.as_view(), name="dashboard_explicit"),
    path("leadership-photos/", views.AdminLeadershipPhotosView.as_view(), name="leadership_photos"),
    path("hero-banner/", views.AdminHeroBannerView.as_view(), name="hero_banner"),

    # Pledges
    path("pledges/", views.AdminPledgeListView.as_view(), name="pledges"),
    path("pledges/sample/", views.AdminPledgeSampleExcelView.as_view(), name="sample_pledges_excel"),
    path("pledges/upload/", views.AdminPledgeUploadExcelView.as_view(), name="upload_pledges_excel"),
    path("pledges/organizations/", views.AdminAssociateOrganizationsView.as_view(), name="associate_orgs"),

    # Students
    path("students/", views.AdminStudentListView.as_view(), name="students"),
    path("students/<uuid:pk>/action/", views.AdminStudentActionView.as_view(), name="student_action"),

    # Organizations
    path("organizations/", views.AdminOrgListView.as_view(), name="organizations"),
    path("organizations/types/", views.AdminOrganizationTypesView.as_view(), name="org_types"),
    path("organizations/<int:pk>/action/", views.AdminOrgActionView.as_view(), name="org_action"),

    # Gallery
    path("gallery/", views.AdminGalleryView.as_view(), name="gallery"),
    path("gallery/<uuid:photo_id>/action/", views.AdminPhotoActionView.as_view(), name="photo_action"),

    # Events
    path("events/", views.AdminEventsView.as_view(), name="events"),
    path("events/<uuid:pk>/toggle/", views.AdminEventTogglePublishView.as_view(), name="event_toggle"),

    # News
    path("news/", views.AdminNewsView.as_view(), name="news"),
    path("news/<uuid:pk>/toggle/", views.AdminNewsTogglePublishView.as_view(), name="news_toggle"),

    # Analytics
    path("analytics/", views.AdminAnalyticsView.as_view(), name="analytics"),

    # Settings & Branding
    path("settings/", views.AdminSettingsView.as_view(), name="settings"),
    path("branding/header-logos/", views.AdminBrandingHeaderLogosView.as_view(), name="branding_header_logos"),
    # Har Ghar Tiranga
    path("har-ghar-tiranga/registrations/", views.AdminHarGharTirangaRegistrationsView.as_view(), name="tiranga_registrations"),
    path("har-ghar-tiranga/registrations/sample/", views.AdminTirangaSampleExcelView.as_view(), name="sample_tiranga_excel"),
    path("har-ghar-tiranga/registrations/upload/", views.AdminTirangaUploadExcelView.as_view(), name="upload_tiranga_excel"),

    # Exports — Excel
    path("export/pledges/excel/", views.AdminExportPledgesExcelView.as_view(), name="export_pledges_excel"),
    path("export/students/excel/", views.AdminExportStudentsExcelView.as_view(), name="export_students_excel"),
    path("export/organizations/excel/", views.AdminExportOrgsExcelView.as_view(), name="export_orgs_excel"),
    path("export/har-ghar-tiranga/excel/", views.AdminExportHarGharTirangaExcelView.as_view(), name="export_tiranga_excel"),

    # Exports — CSV
    path("export/pledges/csv/", views.AdminExportPledgesCSVView.as_view(), name="export_pledges_csv"),
]
