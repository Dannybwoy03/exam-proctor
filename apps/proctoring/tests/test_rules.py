from django.test import SimpleTestCase, override_settings

from ml.yolo_service.detector import Detection
from ml.yolo_service.pose import PosePerson
from ml.yolo_service.rules import evaluate_frame, is_looking_away

from apps.proctoring.models import ViolationLog


@override_settings(
    PROCTORING={
        "MULTIPLE_PERSON_MIN": 2,
        "MULTIPLE_PERSON_CONSECUTIVE_FRAMES": 2,
        "ABSENT_CONSECUTIVE_FRAMES": 2,
        "HEAD_TURN_NOSE_OFFSET_RATIO": 0.15,
    }
)
class ProctoringRulesTests(SimpleTestCase):
    def test_phone_detection_maps_to_phone_violation(self):
        detections = [
            Detection(0, "person", 0.9, 0.2, 0.2, 0.3, 0.5),
            Detection(
                class_id=67,
                label="cell phone",
                confidence=0.92,
                x=0.1,
                y=0.2,
                w=0.1,
                h=0.2,
            ),
        ]
        violations, streak, _ = evaluate_frame(detections, [], absent_streak=0)
        self.assertEqual(streak, 0)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].violation_type, ViolationLog.ViolationType.PHONE)

    def test_absent_after_consecutive_empty_frames(self):
        violations, streak, _ = evaluate_frame([], [], absent_streak=1)
        self.assertEqual(streak, 2)
        self.assertEqual(violations[0].violation_type, ViolationLog.ViolationType.ABSENT)

    def _two_person_frame(self):
        return [
            Detection(0, "person", 0.9, 0.1, 0.1, 0.2, 0.4),
            Detection(0, "person", 0.88, 0.5, 0.1, 0.2, 0.4),
        ]

    def test_single_multi_person_frame_is_not_a_strike(self):
        # One glitchy frame (e.g. a raised phone splitting the body into two
        # person boxes) must not fire the multiple-person rule on its own.
        violations, _, mp_streak = evaluate_frame(
            self._two_person_frame(), [], absent_streak=0, multi_person_streak=0
        )
        types = {v.violation_type for v in violations}
        self.assertNotIn(ViolationLog.ViolationType.MULTIPLE_FACES, types)
        self.assertEqual(mp_streak, 1)

    def test_multiple_persons_flagged_after_consecutive_frames(self):
        violations, _, mp_streak = evaluate_frame(
            self._two_person_frame(), [], absent_streak=0, multi_person_streak=1
        )
        types = {v.violation_type for v in violations}
        self.assertIn(ViolationLog.ViolationType.MULTIPLE_FACES, types)
        self.assertEqual(mp_streak, 2)

    def test_multi_person_streak_resets_when_alone(self):
        detections = [Detection(0, "person", 0.9, 0.2, 0.2, 0.3, 0.5)]
        _, _, mp_streak = evaluate_frame(
            detections, [], absent_streak=0, multi_person_streak=1
        )
        self.assertEqual(mp_streak, 0)

    def _turned_head_pose(self):
        kpts = [[0.5, 0.2, 0.9]] * 17
        kpts[0] = [0.9, 0.2, 0.9]
        kpts[5] = [0.4, 0.4, 0.9]
        kpts[6] = [0.6, 0.4, 0.9]
        return [PosePerson(person_index=0, keypoints=kpts)]

    def test_look_away_is_detected_per_frame(self):
        # The per-frame signal must fire for a clearly turned head...
        self.assertTrue(is_looking_away(self._turned_head_pose()))

    def test_look_away_is_not_an_immediate_violation(self):
        # ...but a single look-away frame is NOT a strike on its own. The
        # sustained 5s timer (in the task layer) owns that decision now.
        violations, _, _ = evaluate_frame([], self._turned_head_pose(), absent_streak=0)
        types = {v.violation_type for v in violations}
        self.assertNotIn(ViolationLog.ViolationType.FACE_OBSTRUCTED, types)

    def test_low_confidence_pose_is_not_look_away(self):
        kpts = [[0.9, 0.2, 0.1]] * 17  # low landmark confidence
        kpts[5] = [0.4, 0.4, 0.1]
        kpts[6] = [0.6, 0.4, 0.1]
        poses = [PosePerson(person_index=0, keypoints=kpts)]
        self.assertFalse(is_looking_away(poses))
