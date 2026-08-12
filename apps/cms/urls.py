"""CMS URL configuration."""

from django.urls import path

from apps.cms import views

app_name = "cms"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="home"),
    path("mission/", views.AboutPageView.as_view(), name="mission"),
    path("contact/", views.ContactPageView.as_view(), name="contact"),
    path("progress/", views.ImpactPageView.as_view(), name="progress"),
    path("privacy/", views.PrivacyPageView.as_view(), name="privacy"),
    path("terms/", views.TermsPageView.as_view(), name="terms"),
    path("green-naroda/", views.GreenNarodaPageView.as_view(), name="green_naroda"),
    path("clean-naroda/", views.CleanNarodaPageView.as_view(), name="clean_naroda"),
    path("har-ghar-tiranga/register/", views.HarGharTirangaRegistrationView.as_view(), name="register_har_ghar_tiranga"),
]
