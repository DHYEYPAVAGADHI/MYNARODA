from django.urls import path
from apps.gallery import views

app_name = "gallery"

urlpatterns = [
    path("", views.GalleryListView.as_view(), name="list"),
    path("submit/", views.SubmitPhotoView.as_view(), name="submit"),
]
