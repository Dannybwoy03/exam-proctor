"""Orchestrate decode → detect → pose → iris gaze → violation candidates."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import cv2
import numpy as np

from .detector import Detection, run_detection
from .pose import PosePerson, run_pose
from .rules import ViolationCandidate, combined_looking_away, evaluate_frame

logger = logging.getLogger(__name__)


@dataclass
class FrameAnalysisResult:
    frame_bytes: bytes
    image_bgr: np.ndarray
    frame_width: int
    frame_height: int
    detections: list[Detection] = field(default_factory=list)
    poses: list[PosePerson] = field(default_factory=list)
    violations: list[ViolationCandidate] = field(default_factory=list)
    absent_streak: int = 0
    multi_person_streak: int = 0
    looking_away: bool = False
    # Iris gaze metrics (None when gaze wasn't measured this frame).
    gaze_h_ratio: float | None = None
    gaze_v_ratio: float | None = None
    gaze_off_screen: bool = False
    inference_ms: float = 0.0


def decode_image_bgr(frame_bytes: bytes) -> np.ndarray | None:
    arr = np.frombuffer(frame_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return image


def analyze_frame(
    frame_bytes: bytes,
    *,
    absent_streak: int = 0,
    multi_person_streak: int = 0,
    run_pose_if_person: bool = True,
) -> FrameAnalysisResult | None:
    import time

    started = time.perf_counter()
    image = decode_image_bgr(frame_bytes)
    if image is None:
        return None

    h, w = image.shape[:2]
    detections = run_detection(image)

    poses: list[PosePerson] = []
    persons = [d for d in detections if d.class_id == 0]
    if run_pose_if_person and persons:
        poses = run_pose(image)

    violations, absent_streak, multi_person_streak = evaluate_frame(
        detections, poses, absent_streak, multi_person_streak
    )

    # Iris gaze runs only when a person is on screen (same gating as pose) and
    # on the head crop of the largest person box — smaller input keeps the
    # extra inference cheap. Any gaze failure degrades to pose-only look-away.
    gaze = None
    if persons:
        try:
            from ml.gaze_service.iris import run_iris_gaze

            largest = max(persons, key=lambda d: d.w * d.h)
            gaze = run_iris_gaze(
                image, face_box=(largest.x, largest.y, largest.w, largest.h)
            )
        except Exception:
            logger.warning("Iris gaze failed for this frame", exc_info=True)

    looking_away = combined_looking_away(poses, gaze)
    elapsed_ms = (time.perf_counter() - started) * 1000

    return FrameAnalysisResult(
        frame_bytes=frame_bytes,
        image_bgr=image,
        frame_width=w,
        frame_height=h,
        detections=detections,
        poses=poses,
        violations=violations,
        absent_streak=absent_streak,
        multi_person_streak=multi_person_streak,
        looking_away=looking_away,
        gaze_h_ratio=gaze.h_ratio if gaze else None,
        gaze_v_ratio=gaze.v_ratio if gaze else None,
        gaze_off_screen=bool(gaze and gaze.off_screen),
        inference_ms=elapsed_ms,
    )
