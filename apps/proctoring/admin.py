from django.contrib import admin

from .models import IDVerificationAttempt, ProctoringSession, ViolationLog, ViolationSnapshot


@admin.register(ProctoringSession)
class ProctoringSessionAdmin(admin.ModelAdmin):
    list_display = ("attempt", "strike_count", "id_verification_status", "lockdown_active")


@admin.register(ViolationLog)
class ViolationLogAdmin(admin.ModelAdmin):
    list_display = ("session", "violation_type", "strike_number", "action_taken", "created_at")
    list_filter = ("violation_type", "action_taken")


admin.site.register(IDVerificationAttempt)
admin.site.register(ViolationSnapshot)
