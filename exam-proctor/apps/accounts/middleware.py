from django.shortcuts import redirect
from django.urls import reverse

from .models import StudentProfile, User


COMMON_EXEMPT_PREFIXES = (
    "/login/",
    "/register/",
    "/logout/",
    "/admin/",
    "/static/",
    # /media/ requests are themselves authenticated + role-gated by the
    # serve_media view in apps/accounts/media.py. They must bypass these
    # status-gate middlewares so that users still on a pending/review page
    # can load their own files (e.g. the ID image they uploaded).
    "/media/",
)


class TeacherApprovalMiddleware:
    """Block unapproved teachers from non-auth pages."""

    EXEMPT_PREFIXES = COMMON_EXEMPT_PREFIXES + ("/pending-approval/",)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.role == User.Role.TEACHER:
            path = request.path
            if not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
                profile = getattr(request.user, "teacher_profile", None)
                if profile and profile.approval_status != profile.ApprovalStatus.APPROVED:
                    pending_url = reverse("accounts:pending_approval")
                    if path != pending_url:
                        return redirect("accounts:pending_approval")
        return self.get_response(request)


class StudentIDReviewMiddleware:
    """Block students with pending/rejected ID reviews from regular pages."""

    EXEMPT_PREFIXES = COMMON_EXEMPT_PREFIXES + ("/id-review/",)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.role == User.Role.STUDENT:
            path = request.path
            if not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
                profile = getattr(request.user, "student_profile", None)
                if (
                    profile
                    and profile.id_review_status
                    != StudentProfile.IDReviewStatus.APPROVED
                ):
                    review_url = reverse("accounts:id_review_pending")
                    if path != review_url:
                        return redirect("accounts:id_review_pending")
        return self.get_response(request)
