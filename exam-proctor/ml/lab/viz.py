"""Overlay drawing for the Model Lab: bounding boxes + pose skeletons.

Works on a BGR ``numpy`` image (OpenCV convention). ``Detection`` boxes and
``PosePerson`` keypoints are normalized to [0, 1] by the pipeline, so we
denormalize against the image size before drawing.
"""

from __future__ import annotations

import cv2
import numpy as np

from ml.yolo_service.detector import Detection
from ml.yolo_service.pose import SKELETON_EDGES, PosePerson

# BGR colors keyed by COCO class id. Violation-bearing objects use saturated
# colors; benign/contextual objects (tv/mouse/remote) use a muted gray-purple so
# they read as "seen but not a strike".
_CLASS_COLORS = {
    0: (0, 200, 0),      # person   - green
    62: (150, 100, 150), # tv       - muted (contextual)
    63: (0, 165, 255),   # laptop   - orange
    64: (150, 100, 150), # mouse    - muted (benign)
    65: (150, 100, 150), # remote   - muted (benign / phone-confusable)
    66: (0, 165, 255),   # keyboard - orange
    67: (0, 0, 255),     # phone    - red
    73: (255, 0, 0),     # book     - blue
}
_DEFAULT_COLOR = (200, 200, 200)
_SKELETON_COLOR = (255, 255, 0)   # cyan-ish for joints/limbs
_KEYPOINT_COLOR = (0, 255, 255)


def draw_detections(
    image_bgr: np.ndarray,
    detections: list[Detection],
    *,
    show_labels: bool = True,
) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    for det in detections:
        x1 = int(det.x * w)
        y1 = int(det.y * h)
        x2 = int((det.x + det.w) * w)
        y2 = int((det.y + det.h) * h)
        color = _CLASS_COLORS.get(det.class_id, _DEFAULT_COLOR)
        cv2.rectangle(image_bgr, (x1, y1), (x2, y2), color, 2)
        if show_labels:
            text = f"{det.label} {det.confidence:.2f}"
            (tw, th), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            ty = max(0, y1 - th - baseline - 2)
            cv2.rectangle(
                image_bgr, (x1, ty), (x1 + tw + 4, ty + th + baseline + 2), color, -1
            )
            cv2.putText(
                image_bgr,
                text,
                (x1 + 2, ty + th),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
    return image_bgr


def draw_poses(
    image_bgr: np.ndarray,
    poses: list[PosePerson],
    *,
    kpt_conf_thresh: float = 0.3,
) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    for person in poses:
        kpts = person.keypoints
        pts: list[tuple[int, int] | None] = []
        for kx, ky, kc in kpts:
            if kc >= kpt_conf_thresh:
                pts.append((int(kx * w), int(ky * h)))
            else:
                pts.append(None)

        for a, b in SKELETON_EDGES:
            if a < len(pts) and b < len(pts) and pts[a] and pts[b]:
                cv2.line(image_bgr, pts[a], pts[b], _SKELETON_COLOR, 2, cv2.LINE_AA)

        for pt in pts:
            if pt:
                cv2.circle(image_bgr, pt, 3, _KEYPOINT_COLOR, -1, cv2.LINE_AA)
    return image_bgr


def draw_overlays(
    image_bgr: np.ndarray,
    detections: list[Detection],
    poses: list[PosePerson],
    *,
    show_boxes: bool = True,
    show_skeleton: bool = True,
    show_labels: bool = True,
    copy: bool = True,
) -> np.ndarray:
    """Return a frame with the requested overlays drawn on it."""
    out = image_bgr.copy() if copy else image_bgr
    if show_skeleton and poses:
        out = draw_poses(out, poses)
    if show_boxes and detections:
        out = draw_detections(out, detections, show_labels=show_labels)
    return out


def to_rgb(image_bgr: np.ndarray) -> np.ndarray:
    """Convert BGR (OpenCV) to RGB for Streamlit's st.image."""
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
