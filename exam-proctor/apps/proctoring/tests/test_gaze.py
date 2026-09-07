"""Tests for iris gaze math and its fusion with the head-turn signal.

These test only the mediapipe-free layers (compute_gaze_ratios,
is_gaze_off_screen, combined_looking_away) so the suite runs without
mediapipe installed.
"""

from django.test import SimpleTestCase, override_settings

from ml.gaze_service.iris import (
    LEFT_EYE_BOTTOM,
    LEFT_EYE_INNER,
    LEFT_EYE_OUTER,
    LEFT_EYE_TOP,
    LEFT_IRIS_CENTER,
    MIN_LANDMARKS,
    RIGHT_EYE_BOTTOM,
    RIGHT_EYE_INNER,
    RIGHT_EYE_OUTER,
    RIGHT_EYE_TOP,
    RIGHT_IRIS_CENTER,
    compute_gaze_ratios,
)
from ml.yolo_service.pose import PosePerson
from ml.yolo_service.rules import combined_looking_away, is_gaze_off_screen

PROCTORING_TEST_SETTINGS = {
    "HEAD_TURN_NOSE_OFFSET_RATIO": 0.15,
    "IRIS_H_RATIO_MIN": 0.25,
    "IRIS_H_RATIO_MAX": 0.75,
    "IRIS_V_RATIO_MAX": 0.80,
}


def _synthetic_landmarks(h_position: float, v_position: float):
    """Build a 478-point landmark list where both irises sit at the given
    fractional position within their eye spans (0=inner/top edge used as the
    low bound, 1=the high bound)."""
    points = [(0.5, 0.5)] * MIN_LANDMARKS

    # Right eye spans x 0.30 -> 0.40 (outer -> inner), y 0.44 -> 0.48 (top -> bottom)
    points[RIGHT_EYE_OUTER] = (0.30, 0.46)
    points[RIGHT_EYE_INNER] = (0.40, 0.46)
    points[RIGHT_EYE_TOP] = (0.35, 0.44)
    points[RIGHT_EYE_BOTTOM] = (0.35, 0.48)
    points[RIGHT_IRIS_CENTER] = (
        0.30 + 0.10 * h_position,
        0.44 + 0.04 * v_position,
    )

    # Left eye spans x 0.60 -> 0.70 (inner -> outer), y 0.44 -> 0.48
    points[LEFT_EYE_INNER] = (0.60, 0.46)
    points[LEFT_EYE_OUTER] = (0.70, 0.46)
    points[LEFT_EYE_TOP] = (0.65, 0.44)
    points[LEFT_EYE_BOTTOM] = (0.65, 0.48)
    points[LEFT_IRIS_CENTER] = (
        0.60 + 0.10 * h_position,
        0.44 + 0.04 * v_position,
    )
    return points


class _StubGaze:
    def __init__(self, off_screen):
        self.off_screen = off_screen


class GazeRatioTests(SimpleTestCase):
    def test_centered_gaze_yields_half_ratios(self):
        h, v = compute_gaze_ratios(_synthetic_landmarks(0.5, 0.5))
        self.assertAlmostEqual(h, 0.5, places=3)
        self.assertAlmostEqual(v, 0.5, places=3)

    def test_iris_at_eye_corner_yields_extreme_ratio(self):
        h, _ = compute_gaze_ratios(_synthetic_landmarks(0.05, 0.5))
        self.assertLess(h, 0.1)
        h, _ = compute_gaze_ratios(_synthetic_landmarks(0.95, 0.5))
        self.assertGreater(h, 0.9)

    def test_looking_down_raises_vertical_ratio(self):
        _, v = compute_gaze_ratios(_synthetic_landmarks(0.5, 0.95))
        self.assertGreater(v, 0.9)

    def test_too_few_landmarks_returns_none(self):
        self.assertIsNone(compute_gaze_ratios([(0.5, 0.5)] * 100))
        self.assertIsNone(compute_gaze_ratios(None))

    def test_degenerate_eye_span_returns_none(self):
        points = _synthetic_landmarks(0.5, 0.5)
        # Collapse both eyes horizontally and vertically -> zero spans.
        for idx in (RIGHT_EYE_OUTER, RIGHT_EYE_INNER, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM):
            points[idx] = (0.35, 0.46)
        for idx in (LEFT_EYE_INNER, LEFT_EYE_OUTER, LEFT_EYE_TOP, LEFT_EYE_BOTTOM):
            points[idx] = (0.65, 0.46)
        self.assertIsNone(compute_gaze_ratios(points))


@override_settings(PROCTORING=PROCTORING_TEST_SETTINGS)
class GazeOffScreenTests(SimpleTestCase):
    def test_centered_gaze_is_on_screen(self):
        self.assertFalse(is_gaze_off_screen(0.5, 0.5))

    def test_horizontal_extremes_are_off_screen(self):
        self.assertTrue(is_gaze_off_screen(0.10, 0.5))
        self.assertTrue(is_gaze_off_screen(0.90, 0.5))

    def test_looking_down_is_off_screen(self):
        self.assertTrue(is_gaze_off_screen(0.5, 0.95))

    def test_explicit_thresholds_override_settings(self):
        self.assertTrue(is_gaze_off_screen(0.40, 0.5, h_min=0.45))
        self.assertFalse(is_gaze_off_screen(0.40, 0.5, h_min=0.30))


@override_settings(PROCTORING=PROCTORING_TEST_SETTINGS)
class LookAwayFusionTests(SimpleTestCase):
    def _turned_head_pose(self):
        kpts = [[0.5, 0.2, 0.9]] * 17
        kpts[0] = [0.9, 0.2, 0.9]   # nose far from shoulder midpoint
        kpts[5] = [0.4, 0.4, 0.9]
        kpts[6] = [0.6, 0.4, 0.9]
        return [PosePerson(person_index=0, keypoints=kpts)]

    def _forward_head_pose(self):
        kpts = [[0.5, 0.2, 0.9]] * 17
        kpts[5] = [0.4, 0.4, 0.9]
        kpts[6] = [0.6, 0.4, 0.9]
        return [PosePerson(person_index=0, keypoints=kpts)]

    def test_neither_signal_means_not_looking_away(self):
        self.assertFalse(
            combined_looking_away(self._forward_head_pose(), _StubGaze(False))
        )

    def test_head_turn_alone_triggers(self):
        self.assertTrue(combined_looking_away(self._turned_head_pose(), None))

    def test_gaze_alone_triggers(self):
        self.assertTrue(
            combined_looking_away(self._forward_head_pose(), _StubGaze(True))
        )

    def test_both_signals_trigger(self):
        self.assertTrue(
            combined_looking_away(self._turned_head_pose(), _StubGaze(True))
        )

    def test_unmeasured_gaze_never_triggers(self):
        self.assertFalse(combined_looking_away(self._forward_head_pose(), None))
        self.assertFalse(combined_looking_away([], None))
