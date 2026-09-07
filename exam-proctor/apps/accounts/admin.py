from django.contrib import admin

from .models import AdminProfile, StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "staff_id_number", "approval_status", "department", "id_card_verified", "approved_at")
    list_filter = ("approval_status", "id_card_verified")
    search_fields = ("staff_id_number", "user__username", "department")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "student_id_number", "programme", "id_card_verified")
    search_fields = ("student_id_number", "user__username", "programme")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
