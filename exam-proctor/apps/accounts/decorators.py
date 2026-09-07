from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import User


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles and not (
                request.user.is_superuser and User.Role.ADMIN in roles
            ):
                raise PermissionDenied
            if User.Role.TEACHER in roles and request.user.role == User.Role.TEACHER:
                profile = getattr(request.user, "teacher_profile", None)
                if profile and profile.approval_status != profile.ApprovalStatus.APPROVED:
                    return redirect("accounts:pending_approval")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
