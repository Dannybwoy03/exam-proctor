from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_choose, name="login"),
    path("login/student/", views.StudentLoginView.as_view(), name="login_student"),
    path("login/teacher/", views.TeacherLoginView.as_view(), name="login_teacher"),
    path("login/admin/", views.AdminLoginView.as_view(), name="login_admin"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.register_choose, name="register"),
    path("register/student/", views.register, {"role": "student"}, name="register_student"),
    path("register/teacher/", views.register, {"role": "teacher"}, name="register_teacher"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("pending-approval/", views.pending_approval, name="pending_approval"),
    path("id-review/", views.id_review_pending, name="id_review_pending"),
    path("admin/teachers/pending/", views.pending_teachers, name="pending_teachers"),
    path("admin/teachers/active/", views.active_teachers, name="active_teachers"),
    path("admin/users/", views.user_list, name="user_list"),
    path("admin/users/create/<str:role>/", views.admin_user_create, name="user_create"),
    path("admin/users/<int:pk>/revoke/", views.admin_user_revoke, name="user_revoke"),
    path("admin/teachers/<int:pk>/review/", views.review_teacher, name="review_teacher"),
    path("admin/teachers/<int:pk>/approve/", views.approve_teacher, name="approve_teacher"),
    path("admin/students/pending-ids/", views.pending_student_ids, name="pending_student_ids"),
    path("admin/students/<int:pk>/review/", views.review_student, name="review_student"),
]
