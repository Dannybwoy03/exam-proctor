from django.contrib import admin

from .models import Course, StudyMaterial


class StudyMaterialInline(admin.TabularInline):
    model = StudyMaterial
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "teacher", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "title")
    inlines = [StudyMaterialInline]


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "uploaded_at")
