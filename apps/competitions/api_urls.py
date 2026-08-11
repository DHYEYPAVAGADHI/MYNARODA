from django.urls import path
from .api_views import OrganizationCertificateLookupView

app_name = "competitions-api"

urlpatterns = [
    path('organization/certificate/', OrganizationCertificateLookupView.as_view(), name='org_certificate_lookup'),
]
