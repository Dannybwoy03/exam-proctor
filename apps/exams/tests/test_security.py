"""Regression tests for exam integrity hardening.

Covers: ended-attempt take/save gates, Cache-Control, result mid-attempt block,
deadline expiry, disconnect-pause not writable, ID verify fail-closed / no resurrect.
"""

from __future__ import annotations

import base64
import shutil
import tempfile
from datetime import timedelta
from io import BytesIO
from unittest import mock

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import StudentProfile, TeacherProfile, User
from apps.courses.models import Course
from apps.exams.models import Exam, ExamAttempt, ExamQuestion, Question, QuestionBank
from apps.proctoring.models import IDVerificationAttempt, ProctoringSession

_MEDIA = tempfile.mkdtemp(prefix="exam_security_media_")


def _jpeg_b64() -> str:
    from PIL import Image

    buf = BytesIO()
    Image.new("RGB", (64, 64), (80, 80, 80)).save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


@override_settings(MEDIA_ROOT=_MEDIA, CELERY_TASK_ALWAYS_EAGER=True)
class ExamSecurityHardeningTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_MEDIA, ignore_errors=True)

    def setUp(self):
        self.student = User.objects.create_user(
            username="stud",
            email="stud@example.com",
            password="pw",
            role=User.Role.STUDENT,
        )
        StudentProfile.objects.create(
            user=self.student,
            student_id_number="20800001",
            face_embedding=[0.1] * 8,
        )
        teacher_user = User.objects.create_user(
            username="teach",
            email="teach@example.com",
            password="pw",
            role=User.Role.TEACHER,
        )
        teacher = TeacherProfile.objects.create(
            user=teacher_user,
            staff_id_number="STF-SEC",
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
        )
        self.course = Course.objects.create(
            code="SEC101", title="Security", teacher=teacher
        )
        now = timezone.now()
        self.exam = Exam.objects.create(
            course=self.course,
            title="Security Exam",
            duration_minutes=30,
            total_marks=10,
            passing_marks=4,
            max_attempts=5,
            is_published=True,
            requires_access_code=False,
            show_results_immediately=True,
            available_from=now - timedelta(hours=1),
            available_until=now + timedelta(days=1),
            approval_status=Exam.ApprovalStatus.APPROVED,
            strictness_level=Exam.StrictnessLevel.LEVEL_1,
            created_by=teacher_user,
        )
        bank = QuestionBank.objects.create(
            course=self.course, title="Bank", created_by=teacher_user
        )
        q = Question.objects.create(
            question_bank=bank,
            text="What is 2+2?",
            question_type=Question.QuestionType.MCQ,
            options=[
                {"key": "A", "label": "3"},
                {"key": "B", "label": "4"},
            ],
            correct_answer={"value": "B"},
            marks=2,
            is_complete=True,
        )
        ExamQuestion.objects.create(exam=self.exam, question=q, order=1)
        self.client = Client(SERVER_NAME="localhost")
        self.client.force_login(self.student)

    def _make_attempt(self, status=ExamAttempt.Status.IN_PROGRESS, **session_kwargs):
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            student=self.student,
            attempt_number=ExamAttempt.objects.filter(
                exam=self.exam, student=self.student
            ).count()
            + 1,
            status=status,
            remaining_seconds=self.exam.effective_duration_minutes * 60,
            started_at=timezone.now(),
        )
        defaults = {
            "id_verification_status": ProctoringSession.IDVerificationStatus.PASSED,
            "lockdown_active": True,
        }
        defaults.update(session_kwargs)
        ProctoringSession.objects.create(attempt=attempt, **defaults)
        return attempt

    def test_take_ended_attempt_redirects_to_result(self):
        attempt = self._make_attempt(status=ExamAttempt.Status.SUBMITTED)
        attempt.ended_at = timezone.now()
        attempt.save(update_fields=["ended_at"])
        url = reverse("exams:take", kwargs={"attempt_id": attempt.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/result/", res["Location"])

    def test_take_response_has_no_store_cache_control(self):
        attempt = self._make_attempt()
        url = reverse("exams:take", kwargs={"attempt_id": attempt.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        cc = res["Cache-Control"]
        self.assertIn("no-store", cc)
        self.assertIn("private", cc)

    def test_save_on_submitted_returns_409(self):
        attempt = self._make_attempt(status=ExamAttempt.Status.SUBMITTED)
        attempt.ended_at = timezone.now()
        attempt.save(update_fields=["ended_at"])
        url = reverse("exams:save", kwargs={"attempt_id": attempt.pk})
        res = self.client.post(url, {})
        self.assertEqual(res.status_code, 409)

    def test_save_on_disconnect_pause_returns_409(self):
        attempt = self._make_attempt(status=ExamAttempt.Status.PAUSED)
        attempt.pause_reason = ExamAttempt.PauseReason.DISCONNECT
        attempt.timer_paused_at = timezone.now()
        attempt.save(update_fields=["pause_reason", "timer_paused_at"])
        url = reverse("exams:save", kwargs={"attempt_id": attempt.pk})
        res = self.client.post(url, {})
        self.assertEqual(res.status_code, 409)
        self.assertFalse(res.json().get("saved"))

    def test_result_blocked_while_in_progress(self):
        attempt = self._make_attempt()
        url = reverse("exams:result", kwargs={"attempt_id": attempt.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        take_url = reverse("exams:take", kwargs={"attempt_id": attempt.pk})
        self.assertIn(take_url, res["Location"])

    def test_deadline_expiry_on_save(self):
        attempt = self._make_attempt()
        attempt.started_at = timezone.now() - timedelta(minutes=90)
        attempt.save(update_fields=["started_at"])
        url = reverse("exams:save", kwargs={"attempt_id": attempt.pk})
        res = self.client.post(url, {})
        self.assertEqual(res.status_code, 409)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.Status.EXPIRED)

    def test_id_verify_refused_when_not_pending_id(self):
        attempt = self._make_attempt(status=ExamAttempt.Status.IN_PROGRESS)
        url = reverse("proctoring:id_verify")
        res = self.client.post(
            url,
            data=f'{{"attempt_id": {attempt.pk}, "frame_base64": "{_jpeg_b64()}"}}',
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 409)

    def test_id_verify_refused_when_already_failed(self):
        attempt = self._make_attempt(
            status=ExamAttempt.Status.PENDING_ID,
            id_verification_status=ProctoringSession.IDVerificationStatus.FAILED,
            lockdown_active=False,
        )
        url = reverse("proctoring:id_verify")
        res = self.client.post(
            url,
            data=f'{{"attempt_id": {attempt.pk}, "frame_base64": "{_jpeg_b64()}"}}',
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 409)

    def test_id_verify_missing_profile_fails_closed(self):
        StudentProfile.objects.filter(user=self.student).delete()
        attempt = self._make_attempt(
            status=ExamAttempt.Status.PENDING_ID,
            id_verification_status=ProctoringSession.IDVerificationStatus.PENDING,
            lockdown_active=False,
        )
        from apps.proctoring.tasks import verify_id_card

        verify_id_card(attempt.pk, _jpeg_b64())
        attempt.refresh_from_db()
        session = attempt.proctoring_session
        session.refresh_from_db()
        self.assertNotEqual(
            session.id_verification_status, ProctoringSession.IDVerificationStatus.PASSED
        )
        self.assertNotEqual(attempt.status, ExamAttempt.Status.IN_PROGRESS)
        self.assertTrue(
            IDVerificationAttempt.objects.filter(
                session=session, status=IDVerificationAttempt.Status.FAILED
            ).exists()
        )

    def test_id_verify_cannot_resurrect_terminated(self):
        attempt = self._make_attempt(
            status=ExamAttempt.Status.TERMINATED,
            id_verification_status=ProctoringSession.IDVerificationStatus.FAILED,
            lockdown_active=False,
        )
        attempt.ended_at = timezone.now()
        attempt.save(update_fields=["ended_at"])
        from apps.proctoring.tasks import verify_id_card

        with mock.patch(
            "ml.id_verification.exam_verify.verify_exam_id_frame"
        ) as mock_verify:
            mock_verify.return_value = mock.Mock(
                passed=True, id_confidence=0.9, face_match_score=0.9, errors=[]
            )
            verify_id_card(attempt.pk, _jpeg_b64())
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.Status.TERMINATED)
