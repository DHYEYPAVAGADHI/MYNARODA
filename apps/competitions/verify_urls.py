from django.urls import path
from .views import VerifyOrganizationCertificateView

app_name = "competitions-verify"

urlpatterns = [
    path('', VerifyOrganizationCertificateView.as_view(), name='verify'),
]
