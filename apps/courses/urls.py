from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="list"),
    path("create/", views.course_create, name="create"),
    path("<int:course_id>/materials/", views.student_materials, name="student_materials"),
]
