from django.urls import path
from .views import CompetitionRegistrationView

app_name = "competitions"

urlpatterns = [
    path("", CompetitionRegistrationView.as_view(), name="registration"),
]
