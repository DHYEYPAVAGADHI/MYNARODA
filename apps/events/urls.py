from django.urls import path
from apps.events import views

app_name = "events"

urlpatterns = [
    path("", views.EventListView.as_view(), name="list"),
    path("<slug:slug>/", views.EventDetailView.as_view(), name="detail"),
    path("<slug:slug>/register/", views.EventRegisterView.as_view(), name="register"),
]
