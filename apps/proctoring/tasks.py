from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.utils import timezone

from apps.exams.models import ExamAttempt

from .models import IDVerificationAttempt, ProctoringSession, ViolationLog
from .services import handle_violation, mock_yolo_detect


def push_ws(attempt_id, payload):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"proctoring_{attempt_id}",
            {"type": "proctoring.event", "payload": payload},
        )


@shared_task
def process_proctor_frame(attempt_id, frame_b64):
    session = ProctoringSession.objects.select_related("attempt__exam").get(
        attempt_id=attempt_id
    )
    if session.attempt.status != ExamAttempt.Status.IN_PROGRESS:
        return

    detections = mock_yolo_detect(frame_b64)
    session.last_frame_at = timezone.now()
    session.save(update_fields=["last_frame_at"])

    for det in detections:
        result = handle_violation(
            session,
            det["type"],
            confidence=det.get("confidence", 0.9),
            reason="AI-detected integrity violation",
        )
        if not result:
            continue
        push_ws(
            attempt_id,
            {
                "type": "warning",
                "strike": result["strike"],
                "max_strikes": result["max_strikes"],
                "violation_type": det["type"],
                "action": result["action"],
            },
        )
        if result.get("terminated") or (
            result["action"] == ViolationLog.ActionTaken.TERMINATE
        ):
            push_ws(
                attempt_id,
                {"type": "terminate", "reason": "Maximum violations exceeded"},
            )


@shared_task
def verify_id_card(attempt_id, frame_b64):
    """Mock ID + face verification for Phase 2; real ML in Phase 3."""
    session = ProctoringSession.objects.select_related(
        "attempt__student__student_profile"
    ).get(attempt_id=attempt_id)

    session.id_verification_attempts += 1
    passed = True  # auto-pass in mock mode

    IDVerificationAttempt.objects.create(
        session=session,
        id_confidence_score=0.95 if passed else 0.3,
        face_match_score=0.85 if passed else 0.4,
        id_check_passed=passed,
        face_check_passed=passed,
        status=IDVerificationAttempt.Status.PASSED if passed else IDVerificationAttempt.Status.FAILED,
    )

    if passed:
        session.id_verification_status = ProctoringSession.IDVerificationStatus.PASSED
        session.lockdown_active = True
        attempt = session.attempt
        attempt.status = ExamAttempt.Status.IN_PROGRESS
        attempt.save(update_fields=["status"])
        push_ws(attempt_id, {"type": "id_status", "status": "passed"})
    else:
        max_attempts = 3
        if session.id_verification_attempts >= max_attempts:
            session.id_verification_status = ProctoringSession.IDVerificationStatus.FAILED
            push_ws(attempt_id, {"type": "id_status", "status": "failed"})
        else:
            push_ws(attempt_id, {"type": "id_status", "status": "retry"})

    session.save()
