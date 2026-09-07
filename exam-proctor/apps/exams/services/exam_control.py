from django.utils import timezone

from apps.exams.models import Exam, ExamAttempt


def freeze_exam(exam, reason="System outage"):
    exam.is_frozen = True
    exam.frozen_at = timezone.now()
    exam.frozen_reason = reason
    exam.save(update_fields=["is_frozen", "frozen_at", "frozen_reason"])
    ExamAttempt.objects.filter(
        exam=exam,
        status=ExamAttempt.Status.IN_PROGRESS,
    ).update(
        status=ExamAttempt.Status.PAUSED,
        timer_paused_at=timezone.now(),
        pause_reason=ExamAttempt.PauseReason.FREEZE,
    )


def unfreeze_exam(exam):
    exam.is_frozen = False
    exam.frozen_reason = ""
    exam.save(update_fields=["is_frozen", "frozen_reason"])
    # Only resume attempts that were paused *by the freeze*. Attempts paused
    # due to a student disconnect must wait for the student's reconnect ping.
    ExamAttempt.objects.filter(
        exam=exam,
        status=ExamAttempt.Status.PAUSED,
        pause_reason=ExamAttempt.PauseReason.FREEZE,
    ).update(
        status=ExamAttempt.Status.IN_PROGRESS,
        timer_paused_at=None,
        pause_reason="",
    )


def add_exam_time(exam, minutes: int):
    if minutes < 1:
        return
    exam.extra_time_minutes += minutes
    exam.save(update_fields=["extra_time_minutes"])
    extra_seconds = minutes * 60
    for attempt in ExamAttempt.objects.filter(
        exam=exam,
        status__in=[ExamAttempt.Status.IN_PROGRESS, ExamAttempt.Status.PAUSED],
    ):
        if attempt.remaining_seconds is not None:
            attempt.remaining_seconds += extra_seconds
            attempt.save(update_fields=["remaining_seconds"])
