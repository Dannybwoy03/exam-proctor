import base64
import tempfile
from datetime import datetime, timedelta, timezone as dt_tz

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import TeacherProfile, User
from apps.courses.models import Course
from apps.exams.models import Exam, ExamAttempt
from apps.proctoring.models import ProctoringSession, ViolationLog
from apps.proctoring.services import strike_message, update_look_away_state


class LookAwayTimerTests(SimpleTestCase):
    """The sustained look-away decision is a pure function so it can be tested
    without the ML pipeline or the database."""

    BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=dt_tz.utc)

    def test_first_look_away_frame_starts_timer_without_a_strike(self):
        started, struck, due = update_look_away_state(None, False, True, self.BASE, 5)
        self.assertEqual(started, self.BASE)
        self.assertFalse(struck)
        self.assertFalse(due)

    def test_brief_glance_below_threshold_is_not_a_strike(self):
        later = self.BASE + timedelta(seconds=3)
        started, struck, due = update_look_away_state(self.BASE, False, True, later, 5)
        self.assertEqual(started, self.BASE)
        self.assertFalse(due)

    def test_strike_fires_once_threshold_is_crossed(self):
        later = self.BASE + timedelta(seconds=5)
        started, struck, due = update_look_away_state(self.BASE, False, True, later, 5)
        self.assertTrue(due)
        self.assertTrue(struck)

    def test_no_second_strike_within_the_same_episode(self):
        later = self.BASE + timedelta(seconds=12)
        started, struck, due = update_look_away_state(self.BASE, True, True, later, 5)
        self.assertFalse(due)
        self.assertTrue(struck)

    def test_looking_back_resets_the_timer(self):
        started, struck, due = update_look_away_state(self.BASE, True, False, self.BASE, 5)
        self.assertIsNone(started)
        self.assertFalse(struck)
        self.assertFalse(due)


class StrikeMessageTests(SimpleTestCase):
    def test_look_away_message(self):
        self.assertEqual(
            strike_message(ViolationLog.ViolationType.FACE_OBSTRUCTED, 1),
            "Strike 1: do not look away from the screen",
        )

    def test_phone_message(self):
        self.assertEqual(
            strike_message(ViolationLog.ViolationType.PHONE, 2),
            "Strike 2: put your phone away",
        )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ViolationEndpointTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            "stud", email="stud@knust.edu", password="pw", role=User.Role.STUDENT
        )
        self.other_student = User.objects.create_user(
            "stud2", email="stud2@knust.edu", password="pw", role=User.Role.STUDENT
        )
        teacher_user = User.objects.create_user(
            "teach", email="teach@knust.edu", password="pw", role=User.Role.TEACHER
        )
        teacher = TeacherProfile.objects.create(
            user=teacher_user,
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
        )
        course = Course.objects.create(code="CS101", title="Intro", teacher=teacher)
        exam = Exam.objects.create(
            course=course,
            title="Midterm",
            strictness_level=Exam.StrictnessLevel.LEVEL_1,
        )
        self.attempt = ExamAttempt.objects.create(
            exam=exam,
            student=self.student,
            status=ExamAttempt.Status.IN_PROGRESS,
        )
        self.session = ProctoringSession.objects.create(attempt=self.attempt)
        self.violation = ViolationLog.objects.create(
            session=self.session,
            violation_type=ViolationLog.ViolationType.PHONE,
            action_taken=ViolationLog.ActionTaken.WARNING,
            strike_number=1,
        )

    def _jpeg_data_url(self):
        payload = base64.b64encode(b"\xff\xd8\xff\xd9fake-jpeg").decode()
        return f"data:image/jpeg;base64,{payload}"

    def test_acknowledge_sets_timestamp_and_is_idempotent(self):
        self.client.force_login(self.student)
        url = reverse("proctoring:acknowledge_violation")
        res = self.client.post(
            url,
            data={"attempt_id": self.attempt.pk, "violation_id": self.violation.pk},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["acknowledged"])
        self.violation.refresh_from_db()
        first_ack = self.violation.acknowledged_at
        self.assertIsNotNone(first_ack)

        # Re-acknowledging must not move the timestamp.
        self.client.post(
            url,
            data={"attempt_id": self.attempt.pk, "violation_id": self.violation.pk},
            content_type="application/json",
        )
        self.violation.refresh_from_db()
        self.assertEqual(self.violation.acknowledged_at, first_ack)

    def test_clip_upload_stores_frames(self):
        self.client.force_login(self.student)
        url = reverse("proctoring:violation_clip")
        frames = [self._jpeg_data_url() for _ in range(3)]
        res = self.client.post(
            url,
            data={
                "attempt_id": self.attempt.pk,
                "violation_id": self.violation.pk,
                "frames": frames,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["saved"], 3)
        self.assertEqual(self.violation.clip_frames.count(), 3)

    def test_clip_upload_is_idempotent(self):
        self.client.force_login(self.student)
        url = reverse("proctoring:violation_clip")
        body = {
            "attempt_id": self.attempt.pk,
            "violation_id": self.violation.pk,
            "frames": [self._jpeg_data_url()],
        }
        self.client.post(url, data=body, content_type="application/json")
        res = self.client.post(url, data=body, content_type="application/json")
        self.assertTrue(res.json().get("skipped"))
        self.assertEqual(self.violation.clip_frames.count(), 1)

    def test_other_student_cannot_acknowledge(self):
        self.client.force_login(self.other_student)
        res = self.client.post(
            reverse("proctoring:acknowledge_violation"),
            data={"attempt_id": self.attempt.pk, "violation_id": self.violation.pk},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 404)
        self.violation.refresh_from_db()
        self.assertIsNone(self.violation.acknowledged_at)
