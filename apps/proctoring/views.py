import json

from django.conf import settings
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.accounts.portal import render_portal
from apps.exams.models import Exam, ExamAttempt

from .models import ProctoringSession, ViolationLog, ViolationSnapshot
from .services import (
    LOCKDOWN_VIOLATIONS,
    ReviewPermissionError,
    apply_violation_review,
    get_session_for_student,
    handle_violation,
    integrity_index,
    invalidate_attempt,
    risk_level,
)
from .tasks import process_proctor_frame, push_ws, verify_id_card


def _parse_json_body(request):
    """Safely parse a request body as JSON. Returns (data, error_response_or_None)."""
    try:
        return json.loads(request.body or b"{}"), None
    except (ValueError, json.JSONDecodeError):
        return None, JsonResponse({"error": "Malformed JSON body."}, status=400)


@role_required(User.Role.TEACHER)
def flagged_sessions(request):
    # Flagged-session review is a teacher-only responsibility. Admins manage
    # accounts and approvals; they don't audit live exam integrity.
    sessions_qs = ProctoringSession.objects.filter(
        attempt__exam__course__teacher__user=request.user
    )

    flagged = (
        sessions_qs.filter(strike_count__gt=0)
        .select_related("attempt__student", "attempt__exam__course")
        .prefetch_related(
            Prefetch(
                "violations",
                queryset=ViolationLog.objects.order_by("created_at"),
            )
        )
        .annotate(
            violation_count=Count("violations"),
            disputed_count=Count("violations", filter=Q(violations__is_disputed=True)),
        )
        .order_by("-attempt__started_at")
    )

    selected = None
    selected_id = request.GET.get("session")
    flagged_list = []
    for s in flagged:
        level, risk = risk_level(s)
        violations = list(s.violations.all())
        flagged_list.append(
            {
                "session": s,
                "risk_level": level,
                "risk_score": risk,
                "integrity": integrity_index(s),
                "violations": violations,
                "latest_violation": violations[-1] if violations else None,
            }
        )

    if selected_id:
        selected = get_object_or_404(flagged, pk=selected_id)
    elif flagged.exists():
        selected = flagged.first()

    timeline = []
    logs = []
    snapshots = []
    if selected:
        timeline = selected.violations.order_by("created_at")
        for v in timeline:
            logs.append(
                f"[{v.created_at.strftime('%H:%M:%S')}] OBJ_DETECT: {v.violation_type.upper()} "
                f"(confidence: {v.confidence:.2f})"
            )
        snapshots = ViolationSnapshot.objects.filter(
            violation__session=selected
        ).select_related("violation")

    return render_portal(
        request,
        "partials/portal/flagged_sessions.html",
        {
            "flagged_list": flagged_list,
            "selected_session": selected,
            "selected_integrity": integrity_index(selected) if selected else None,
            "timeline": timeline,
            "logs": logs,
            "snapshots": snapshots,
            "portal_nav": "flagged",
            "active_count": flagged.filter(
                attempt__status=ExamAttempt.Status.IN_PROGRESS
            ).count(),
        },
        page_title="Flagged Sessions",
    )


def _attempt_id_key(group, request):
    """Rate-limit key derived from the attempt id in the JSON body.

    Falls back to the user id if the body can't be parsed, so a malicious
    client can't escape the limit by sending malformed payloads.
    """
    try:
        body = json.loads(request.body or b"{}")
        attempt_id = body.get("attempt_id")
        if attempt_id is not None:
            return f"attempt:{attempt_id}"
    except (ValueError, json.JSONDecodeError):
        pass
    return f"user:{getattr(request.user, 'pk', 'anon')}"


@require_POST
@role_required(User.Role.STUDENT)
@ratelimit(key="user", rate="20/m", method="POST", block=True)
def id_verify(request):
    data, err = _parse_json_body(request)
    if err:
        return err
    attempt_id = data.get("attempt_id")
    frame_b64 = data.get("frame_base64", "")
    # Cheap existence + ownership check (avoids loading the whole row when we
    # only need to gate access before queueing the verification task).
    if not ProctoringSession.objects.filter(
        attempt_id=attempt_id, attempt__student=request.user
    ).exists():
        return JsonResponse({"error": "Proctoring session not found."}, status=404)
    verify_id_card.delay(attempt_id, frame_b64)
    return JsonResponse({"accepted": True})


@require_POST
@role_required(User.Role.STUDENT)
@ratelimit(key=_attempt_id_key, rate="20/m", method="POST", block=True)
def process_frame(request):
    data, err = _parse_json_body(request)
    if err:
        return err
    attempt_id = data.get("attempt_id")
    frame_b64 = data.get("frame_base64", "")
    client_events = data.get("client_events", [])

    try:
        session = get_session_for_student(attempt_id, request.user)
    except ProctoringSession.DoesNotExist:
        return JsonResponse({"error": "Proctoring session not found."}, status=404)
    if session.attempt.status != ExamAttempt.Status.IN_PROGRESS:
        return JsonResponse({"error": "Exam not in progress"}, status=400)

    for event in client_events:
        vtype = LOCKDOWN_VIOLATIONS.get(event.get("type"))
        if vtype:
            result = handle_violation(session, vtype, lockdown_event=True)
            if result:
                push_ws(
                    attempt_id,
                    {
                        "type": "warning",
                        "strike": result["strike"],
                        "max_strikes": result["max_strikes"],
                        "violation_type": vtype,
                        "action": result["action"],
                    },
                )
                if result.get("terminated") or (
                    result["action"] == ViolationLog.ActionTaken.TERMINATE
                ):
                    push_ws(
                        attempt_id,
                        {"type": "terminate", "reason": "Lockdown violation"},
                    )

    process_proctor_frame.delay(attempt_id, frame_b64)
    session.refresh_from_db()
    return JsonResponse(
        {
            "accepted": True,
            "session_strikes": session.strike_count,
            "max_strikes": session.max_strikes,
        }
    )


@require_POST
@role_required(User.Role.STUDENT)
def client_event(request):
    data, err = _parse_json_body(request)
    if err:
        return err
    attempt_id = data.get("attempt_id")
    event_type = data.get("type")
    try:
        session = get_session_for_student(attempt_id, request.user)
    except ProctoringSession.DoesNotExist:
        return JsonResponse({"error": "Proctoring session not found."}, status=404)
    vtype = LOCKDOWN_VIOLATIONS.get(event_type)
    if not vtype:
        return JsonResponse({"ignored": True})
    if session.attempt.status != ExamAttempt.Status.IN_PROGRESS:
        return JsonResponse({"ignored": True, "reason": "Attempt not in progress."})

    # Dispatch through the strictness policy. At NONE the call is a no-op; at
    # LEVEL_1 it goes through the 3-strike rule (warnings, then terminate);
    # at LEVEL_2 the first offense terminates immediately.
    reason_label = {
        "tab_switch": "Tab switched during exam",
        "visibility_hidden": "Tab switched during exam",
        "focus_lost": "Window left during exam",
        "exit_fullscreen": "Fullscreen exited during exam",
    }.get(event_type, "Lockdown violation")
    result = handle_violation(
        session, vtype, reason=reason_label, lockdown_event=True
    )
    if result is None:
        return JsonResponse({"ignored": True, "reason": "Strictness=none"})

    terminated = bool(result.get("terminated")) or (
        result.get("action") == ViolationLog.ActionTaken.TERMINATE
    )
    push_ws(
        attempt_id,
        {
            "type": "warning",
            "strike": result["strike"],
            "max_strikes": result["max_strikes"],
            "violation_type": vtype,
            "action": result["action"],
            "reason": reason_label,
        },
    )
    if terminated:
        push_ws(attempt_id, {"type": "terminate", "reason": reason_label})
    session.refresh_from_db()
    return JsonResponse(
        {
            "terminated": terminated,
            "strike": result["strike"],
            "max_strikes": result["max_strikes"],
            "reason": reason_label,
            "strikes": session.strike_count,
        }
    )


@require_POST
@role_required(User.Role.STUDENT)
@ratelimit(key=_attempt_id_key, rate="10/m", method="POST", block=True)
def dispute_latest_violation(request):
    """Mark the student's most recent un-disputed violation as disputed.

    The strike warning dialog shows the latest violation; the student presses
    'File Dispute' to flag it for teacher review. Idempotent — re-pressing the
    button on an already-disputed log is a no-op.
    """
    data, err = _parse_json_body(request)
    if err:
        return err
    attempt_id = data.get("attempt_id")
    try:
        session = get_session_for_student(attempt_id, request.user)
    except ProctoringSession.DoesNotExist:
        return JsonResponse({"error": "Proctoring session not found."}, status=404)

    violation = (
        session.violations.filter(is_disputed=False).order_by("-created_at").first()
    )
    if violation is None:
        return JsonResponse({"disputed": False, "reason": "No violation to dispute."})

    violation.is_disputed = True
    violation.disputed_at = timezone.now()
    violation.save(update_fields=["is_disputed", "disputed_at"])
    return JsonResponse(
        {
            "disputed": True,
            "violation_id": violation.pk,
            "violation_type": violation.violation_type,
            "strike_number": violation.strike_number,
        }
    )


@role_required(User.Role.STUDENT)
def session_status(request, attempt_id):
    try:
        session = get_session_for_student(attempt_id, request.user)
    except ProctoringSession.DoesNotExist:
        return JsonResponse({"error": "Proctoring session not found."}, status=404)
    violations = list(
        session.violations.values("violation_type", "strike_number", "created_at")
    )
    attempt = session.attempt
    return JsonResponse(
        {
            "strike_count": session.strike_count,
            "max_strikes": session.max_strikes,
            "id_verification_status": session.id_verification_status,
            "violations": violations,
            "attempt_status": attempt.status,
            "remaining_seconds": attempt.computed_remaining_seconds,
            "pause_reason": attempt.pause_reason,
        }
    )


def _violation_row_response(request, violation):
    """Re-render the timeline row for the just-edited violation.

    Used by HTMX so the row swaps in-place after the teacher saves changes.
    """
    return render(
        request,
        "partials/portal/violation_row.html",
        {"v": violation},
    )


@require_POST
@role_required(User.Role.TEACHER)
def review_violation(request, pk):
    """Teacher action: status / severity / note update on a single violation.

    Returns the re-rendered row partial for HTMX swap, or a JSON error if the
    teacher doesn't own the underlying exam.
    """
    violation = get_object_or_404(
        ViolationLog.objects.select_related(
            "session__attempt__exam__course__teacher"
        ),
        pk=pk,
    )
    try:
        apply_violation_review(
            violation,
            request.user,
            review_status=request.POST.get("review_status") or None,
            severity=request.POST.get("severity") or None,
            teacher_note=request.POST.get("teacher_note"),
        )
    except ReviewPermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    return _violation_row_response(request, violation)


@require_POST
@role_required(User.Role.TEACHER)
def invalidate_exam_attempt(request, pk):
    """Teacher action: nullify the entire attempt (Disqualify/Nullify).

    Forces score=0 via grade_attempt and returns the refreshed session header
    so HTMX can swap in the new banner without a full page reload.
    """
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related("exam__course__teacher"),
        pk=pk,
    )
    reason = (request.POST.get("reason") or "").strip()
    try:
        invalidate_attempt(attempt, request.user, reason=reason)
    except ReviewPermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    session = attempt.proctoring_session
    return render(
        request,
        "partials/portal/flagged_session_header.html",
        {
            "attempt": attempt,
            "session": session,
            "selected_integrity": integrity_index(session),
        },
    )
