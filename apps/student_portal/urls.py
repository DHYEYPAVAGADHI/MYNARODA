from django.urls import path
from . import views



urlpatterns = [
    path("", views.portal_home, name="student_portal"),
    path("essay/", views.essay_form, name="essay_form"),
    path("drawing/", views.drawing_form, name="drawing_form"),
    path("project/", views.project_form, name="project_form"),
    path("showcase/", views.showcase, name="student_showcase"),
    path("api/submit/", views.api_submit, name="api_submit"),
    path("api/check-mobile/", views.api_check_mobile, name="api_check_mobile"),
]
