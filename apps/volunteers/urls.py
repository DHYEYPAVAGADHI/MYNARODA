from django.urls import path
from apps.volunteers import views

app_name = "volunteers"

urlpatterns = [
    path("", views.VolunteerLeaderboardView.as_view(), name="leaderboard"),
    path("pledge/", views.SubmitPledgeRegistrationView.as_view(), name="pledge_submit"),
    path("track-share/", views.TrackShareView.as_view(), name="track_share"),
]
