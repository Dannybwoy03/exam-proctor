from django.db import models

from apps.exams.models import ExamAttempt


class ProctoringSession(models.Model):
    class IDVerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"

    attempt = models.OneToOneField(
        ExamAttempt, on_delete=models.CASCADE, related_name="proctoring_session"
    )
    strike_count = models.PositiveIntegerField(default=0)
    max_strikes = models.PositiveIntegerField(default=3)
    id_verification_status = models.CharField(
        max_length=20,
        choices=IDVerificationStatus.choices,
        default=IDVerificationStatus.PENDING,
    )
    id_verification_attempts = models.PositiveIntegerField(default=0)
    lockdown_active = models.BooleanField(default=False)
    last_frame_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Proctoring — attempt {self.attempt_id}"


class IDVerificationAttempt(models.Model):
    class Status(models.TextChoices):
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"

    session = models.ForeignKey(
        ProctoringSession, on_delete=models.CASCADE, related_name="id_attempts"
    )
    frame_image = models.ImageField(upload_to="id_verification/", blank=True)
    detected_id_type = models.CharField(max_length=100, blank=True)
    id_confidence_score = models.FloatField(default=0)
    face_match_score = models.FloatField(default=0)
    id_check_passed = models.BooleanField(default=False)
    face_check_passed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)


class ViolationLog(models.Model):
    class ViolationType(models.TextChoices):
        PHONE = "phone", "Mobile Phone"
        BOOK = "book", "Book"
        NOTES = "notes", "Notes"
        ABSENT = "absent", "Student Absent"
        MULTIPLE_FACES = "multiple_faces", "Multiple People"
        FACE_OBSTRUCTED = "face_obstructed", "Face Obstructed"
        TAB_SWITCH = "tab_switch", "Tab Switch"
        FOCUS_LOST = "focus_lost", "Focus Lost"
        EXIT_FULLSCREEN = "exit_fullscreen", "Exit Fullscreen"

    class ActionTaken(models.TextChoices):
        WARNING = "warning", "Warning"
        TERMINATE = "terminate", "Terminate"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class ReviewStatus(models.TextChoices):
        # Teacher adjudication state. PENDING_REVIEW is the default; the
        # teacher transitions to one of the other values via the audit UI.
        PENDING_REVIEW = "pending_review", "Pending Review"
        CONFIRMED = "confirmed", "Confirmed Violation"
        IGNORED = "ignored", "Ignored"
        FALSE_ALARM = "false_alarm", "Resolved — False Alarm"
        ESCALATED = "escalated", "Escalated"

    session = models.ForeignKey(
        ProctoringSession, on_delete=models.CASCADE, related_name="violations"
    )
    violation_type = models.CharField(max_length=30, choices=ViolationType.choices)
    confidence = models.FloatField(default=0)
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.MEDIUM
    )
    severity_overridden = models.BooleanField(
        default=False,
        help_text="True when a teacher manually changed the AI-assigned severity.",
    )
    strike_number = models.PositiveIntegerField(default=1)
    action_taken = models.CharField(max_length=20, choices=ActionTaken.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    # Student-side dispute marker. Set when the student presses "File Dispute"
    # on the strike warning dialog. Teachers see it in the flagged-sessions
    # review and can choose how to weigh the violation.
    is_disputed = models.BooleanField(default=False)
    disputed_at = models.DateTimeField(null=True, blank=True)
    # Teacher-side adjudication.
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING_REVIEW,
    )
    teacher_note = models.TextField(
        blank=True,
        help_text="Optional teacher message shown to the student on their result page.",
    )
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_violations",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["session", "created_at"]),
            models.Index(fields=["review_status"]),
        ]

    @property
    def is_dismissed(self) -> bool:
        """A violation a teacher considers nullified for scoring discussions."""
        return self.review_status in (
            self.ReviewStatus.IGNORED,
            self.ReviewStatus.FALSE_ALARM,
        )


class ViolationSnapshot(models.Model):
    violation = models.OneToOneField(
        ViolationLog, on_delete=models.CASCADE, related_name="snapshot"
    )
    image = models.ImageField(upload_to="violations/")
    bounding_boxes = models.JSONField(default=list, blank=True)
