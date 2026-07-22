"""Iris-based gaze estimation from MediaPipe FaceMesh landmarks.

Detects the case the pose-based look-away rule cannot see: the head stays
forward but the eyes track something off-screen (second monitor, notes).

The ratio math (``compute_gaze_ratios``) is pure and mediapipe-free so it can
be unit-tested with synthetic landmarks; only ``run_iris_gaze`` touches the
model.
"""

from __future__ import annotations

from dataclasses import dataclass

# FaceMesh landmark indices (refine_landmarks=True adds the 10 iris points).
RIGHT_IRIS_CENTER = 468
LEFT_IRIS_CENTER = 473
RIGHT_EYE_OUTER = 33
RIGHT_EYE_INNER = 133
LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263
RIGHT_EYE_TOP = 159
RIGHT_EYE_BOTTOM = 145
LEFT_EYE_TOP = 386
LEFT_EYE_BOTTOM = 374

# Landmarks below this count mean iris refinement is unavailable.
MIN_LANDMARKS = 478


@dataclass
class GazeResult:
    off_screen: bool
    h_ratio: float
    v_ratio: float
    confidence: float


def _span_ratio(value: float, low: float, high: float) -> float | None:
    """Position of ``value`` within [low, high]; centered gaze is ~0.5."""
    span = high - low
    if abs(span) < 1e-6:
        return None
    return (value - low) / span


def compute_gaze_ratios(points) -> tuple[float, float] | None:
    """Average horizontal/vertical iris position across both eyes.

    ``points`` is any sequence indexable by FaceMesh landmark id yielding
    ``(x, y)`` pairs (normalized coordinates). Returns ``(h_ratio, v_ratio)``
    where ~0.5 is a centered gaze, or ``None`` if the landmarks are unusable.
    """
    if points is None or len(points) < MIN_LANDMARKS:
        return None
    try:
        r_h = _span_ratio(
            points[RIGHT_IRIS_CENTER][0],
            points[RIGHT_EYE_OUTER][0],
            points[RIGHT_EYE_INNER][0],
        )
        l_h = _span_ratio(
            points[LEFT_IRIS_CENTER][0],
            points[LEFT_EYE_INNER][0],
            points[LEFT_EYE_OUTER][0],
        )
        r_v = _span_ratio(
            points[RIGHT_IRIS_CENTER][1],
            points[RIGHT_EYE_TOP][1],
            points[RIGHT_EYE_BOTTOM][1],
        )
        l_v = _span_ratio(
            points[LEFT_IRIS_CENTER][1],
            points[LEFT_EYE_TOP][1],
            points[LEFT_EYE_BOTTOM][1],
        )
    except (IndexError, TypeError):
        return None

    h_vals = [v for v in (r_h, l_h) if v is not None]
    v_vals = [v for v in (r_v, l_v) if v is not None]
    if not h_vals or not v_vals:
        return None
    return sum(h_vals) / len(h_vals), sum(v_vals) / len(v_vals)


def _crop_head_region(image_bgr, face_box):
    """Crop the head area from a normalized YOLO person box (x, y, w, h).

    A smaller input makes FaceMesh both faster and more accurate. Falls back
    to the full frame when the crop would be degenerate.
    """
    if face_box is None:
        return image_bgr
    img_h, img_w = image_bgr.shape[:2]
    x, y, w, h = face_box
    head_h = h * 0.45  # head + shoulders live in the top part of a person box
    margin_x = w * 0.10
    margin_y = head_h * 0.15
    x1 = max(0, int((x - margin_x) * img_w))
    y1 = max(0, int((y - margin_y) * img_h))
    x2 = min(img_w, int((x + w + margin_x) * img_w))
    y2 = min(img_h, int((y + head_h + margin_y) * img_h))
    if (x2 - x1) < 32 or (y2 - y1) < 32:
        return image_bgr
    return image_bgr[y1:y2, x1:x2]


def run_iris_gaze(image_bgr, face_box=None) -> GazeResult | None:
    """Estimate gaze direction for one frame.

    Returns ``None`` whenever gaze cannot be measured (model unavailable, no
    face, degenerate landmarks) — never a strike signal by itself, so a gaze
    failure degrades to the pose-only look-away behavior.
    """
    from django.conf import settings

    cfg = settings.PROCTORING
    if cfg.get("USE_MOCK_ML") or not cfg.get("USE_IRIS_GAZE", True):
        return None

    from .loader import get_landmarker

    landmarker = get_landmarker()
    if landmarker is None:
        return None

    import cv2
    import mediapipe as mp
    import numpy as np

    crop = _crop_head_region(image_bgr, face_box)
    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)
    )
    results = landmarker.detect(mp_image)
    if not getattr(results, "face_landmarks", None):
        return None

    landmarks = results.face_landmarks[0]
    points = [(p.x, p.y) for p in landmarks]
    ratios = compute_gaze_ratios(points)
    if ratios is None:
        return None
    h_ratio, v_ratio = ratios

    from ml.yolo_service.rules import is_gaze_off_screen

    return GazeResult(
        off_screen=is_gaze_off_screen(h_ratio, v_ratio),
        h_ratio=h_ratio,
        v_ratio=v_ratio,
        confidence=1.0,
    )
