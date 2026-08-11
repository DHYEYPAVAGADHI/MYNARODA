from django.urls import path
from apps.trees import views

app_name = "trees"

urlpatterns = [
    path("", views.TreeListView.as_view(), name="list"),
    path("plant/", views.PlantTreeView.as_view(), name="plant"),
    path("<uuid:pk>/", views.TreeDetailView.as_view(), name="detail"),
]
