from django.urls import path
from apps.certificates import views

app_name = "certificates"

urlpatterns = [
    path("", views.CertificateListView.as_view(), name="list"),
    path("verify/<str:certificate_number>/", views.CertificateVerifyView.as_view(), name="verify"),
]
