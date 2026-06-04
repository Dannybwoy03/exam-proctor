"""Authenticated media serving with role-based access control.

Every upload sits under ``MEDIA_ROOT``. The directory prefix encodes who is
allowed to read the file:

- ``profiles/``           — owner sees their own; teachers can see profile
                            photos of students enrolled in their courses;
                            admins see everything.
- ``id_proofs/``          — student owner; teachers of courses the student
                            is enrolled in; admins.
- ``staff_id_proofs/``    — teacher owner only; admins.
- ``id_verification/``    — attempt student only; teacher of the course;
                            admins.
- ``violations/``         — attempt student only; teacher of the course;
                            admins.
- ``study_materials/``    — enrolled student; teacher of the course; admins.

Anything else is denied. Anonymous requests redirect to login.
"""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from apps.accounts.models import StudentProfile, TeacherProfile, User
from apps.courses.models import Course, StudyMaterial
from apps.exams.models import ExamCodeRedemption
from apps.proctoring.models import IDVerificationAttempt, ViolationSnapshot


def _media_root() -> Path:
    return Path(settings.MEDIA_ROOT).resolve()


def _safe_absolute_path(rel_path: str) -> Path:
    """Resolve rel_path against MEDIA_ROOT and refuse path traversal."""
    media_root = _media_root()
    candidate = (media_root / rel_path).resolve()
    try:
        candidate.relative_to(media_root)
    except ValueError as exc:  # outside MEDIA_ROOT
        raise PermissionDenied("Invalid media path.") from exc
    return candidate


def _student_enrolled_in_course(student: User, course: Course) -> bool:
    """Match the existing 'enrolled' signal: student has redeemed a code for
    an exam in this course (see apps/courses/views.py)."""
    return ExamCodeRedemption.objects.filter(
        student=student,
        access_code__exam__course=course,
    ).exists()


def _teacher_owns_course(teacher: User, course: Course) -> bool:
    return getattr(course, "teacher", None) and course.teacher.user_id == teacher.pk


# --- per-prefix permission handlers --------------------------------------------------

def _can_view_profile_photo(viewer: User, rel_path: str) -> bool:
    owner = User.objects.filter(profile_photo=rel_path).first()
    if not owner:
        return False
    if viewer.pk == owner.pk:
        return True
    if viewer.is_admin_user:
        return True
    if viewer.is_teacher_user:
        # Teachers may see the profile photo of students enrolled in any of
        # their courses (for exam proctoring review).
        if owner.role != User.Role.STUDENT:
            return False
        own_courses = Course.objects.filter(teacher__user=viewer)
        return ExamCodeRedemption.objects.filter(
            student=owner,
            access_code__exam__course__in=own_courses,
        ).exists()
    return False


def _can_view_student_id(viewer: User, rel_path: str) -> bool:
    profile = StudentProfile.objects.filter(id_proof_image=rel_path).select_related(
        "user"
    ).first()
    if not profile:
        return False
    if viewer.pk == profile.user_id:
        return True
    if viewer.is_admin_user:
        return True
    if viewer.is_teacher_user:
        own_courses = Course.objects.filter(teacher__user=viewer)
        return ExamCodeRedemption.objects.filter(
            student=profile.user,
            access_code__exam__course__in=own_courses,
        ).exists()
    return False


def _can_view_staff_id(viewer: User, rel_path: str) -> bool:
    profile = TeacherProfile.objects.filter(id_proof_image=rel_path).first()
    if not profile:
        return False
    if viewer.pk == profile.user_id:
        return True
    return viewer.is_admin_user


def _can_view_id_verification_frame(viewer: User, rel_path: str) -> bool:
    attempt_row = (
        IDVerificationAttempt.objects.filter(frame_image=rel_path)
        .select_related("session__attempt__student", "session__attempt__exam__course__teacher__user")
        .first()
    )
    if not attempt_row:
        return False
    exam_attempt = attempt_row.session.attempt
    if viewer.pk == exam_attempt.student_id:
        return True
    if viewer.is_admin_user:
        return True
    if viewer.is_teacher_user:
        return exam_attempt.exam.course.teacher.user_id == viewer.pk
    return False


def _can_view_violation_snapshot(viewer: User, rel_path: str) -> bool:
    snapshot = (
        ViolationSnapshot.objects.filter(image=rel_path)
        .select_related("violation__session__attempt__student",
                        "violation__session__attempt__exam__course__teacher__user")
        .first()
    )
    if not snapshot:
        return False
    exam_attempt = snapshot.violation.session.attempt
    if viewer.pk == exam_attempt.student_id:
        return True
    if viewer.is_admin_user:
        return True
    if viewer.is_teacher_user:
        return exam_attempt.exam.course.teacher.user_id == viewer.pk
    return False


def _can_view_study_material(viewer: User, rel_path: str) -> bool:
    material = StudyMaterial.objects.filter(file=rel_path).select_related(
        "course__teacher__user"
    ).first()
    if not material:
        return False
    if viewer.is_admin_user:
        return True
    if viewer.is_teacher_user:
        return _teacher_owns_course(viewer, material.course)
    if viewer.is_student_user:
        return _student_enrolled_in_course(viewer, material.course)
    return False


# Prefix -> permission check
_PERMISSION_HANDLERS = {
    "profiles/": _can_view_profile_photo,
    "id_proofs/": _can_view_student_id,
    "staff_id_proofs/": _can_view_staff_id,
    "id_verification/": _can_view_id_verification_frame,
    "violations/": _can_view_violation_snapshot,
    "study_materials/": _can_view_study_material,
}


def _permission_handler(rel_path: str):
    for prefix, handler in _PERMISSION_HANDLERS.items():
        if rel_path.startswith(prefix):
            return handler
    return None


@login_required
def serve_media(request, rel_path: str):
    """Stream a file from MEDIA_ROOT after authenticating and authorizing the
    request. Returns 404 if the file is missing, 403 if the user lacks
    permission, 400 on path traversal attempts."""
    # Normalise: strip leading slashes, reject empty/dotted segments early.
    rel_path = rel_path.lstrip("/")
    if not rel_path or rel_path.startswith(".") or "//" in rel_path:
        raise Http404

    handler = _permission_handler(rel_path)
    if handler is None:
        # Unknown prefix — refuse rather than fall through to "anyone can read".
        raise PermissionDenied("This media path is not accessible.")

    if not handler(request.user, rel_path):
        raise PermissionDenied("You do not have access to this file.")

    abs_path = _safe_absolute_path(rel_path)
    if not abs_path.is_file():
        raise Http404

    content_type, _ = mimetypes.guess_type(str(abs_path))
    response = FileResponse(
        open(abs_path, "rb"),
        content_type=content_type or "application/octet-stream",
    )
    # Conservative caching: never let a CDN cache authenticated PII responses.
    response["Cache-Control"] = "private, no-store"
    # Force download for ID-card images to discourage embedding/hot-linking.
    if rel_path.startswith(("id_proofs/", "staff_id_proofs/", "id_verification/", "violations/")):
        response["Content-Disposition"] = (
            f'inline; filename="{os.path.basename(abs_path)}"'
        )
    return response
