"""Map detections + pose heuristics to ViolationLog types."""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from apps.proctoring.models import ViolationLog

from .detector import Detection
from .pose import PosePerson


@dataclass
class ViolationCandidate:
    violation_type: str
    confidence: float
    severity: str = ViolationLog.Severity.MEDIUM


# How each reported COCO id maps to a violation. Kept explicit so the detection
# taxonomy (detector.COCO_NAMES) and the exam rules stay in lockstep.
PHONE_COCO_IDS = {67}                 # cell phone -> phone violation (HIGH)
BOOK_COCO_IDS = {73}                  # book / notes -> book violation (MEDIUM)
SECONDARY_DEVICE_COCO_IDS = {63, 66}  # laptop, keyboard -> notes when near a person
# Detected for audit visibility + hard-negative training, but never a strike:
#   tv(62) second screen is contextual; mouse(64) and remote(65) are benign desk
#   objects whose main value is NOT being misread as a phone.
BENIGN_COCO_IDS = {62, 64, 65}


def _person_boxes(detections: list[Detection]) -> list[Detection]:
    return [d for d in detections if d.class_id == 0]


def _box_center(det: Detection) -> tuple[float, float]:
    return det.x + det.w / 2, det.y + det.h / 2


def _boxes_overlap(a: Detection, b: Detection, margin: float = 0.05) -> bool:
    ax2, ay2 = a.x + a.w + margin, a.y + a.h + margin
    bx2, by2 = b.x + b.w + margin, b.y + b.h + margin
    return not (ax2 < b.x - margin or bx2 < a.x - margin or ay2 < b.y - margin or by2 < a.y - margin)


def _device_near_person(device: Detection, persons: list[Detection]) -> bool:
    # No person boxes this frame usually means detection missed the student
    # (occlusion, lighting), not an empty room — don't turn that uncertainty
    # into a NOTES strike. The absent rule handles true empty frames.
    if not persons:
        return False
    cx, cy = _box_center(device)
    for p in persons:
        if p.x <= cx <= p.x + p.w and p.y <= cy <= p.y + p.h:
            return True
        if _boxes_overlap(device, p):
            return True
    return False


def head_turn_offset(person: PosePerson) -> dict | None:
    """Geometry behind the look-away rule, exposed for inspection/calibration.

    Returns ``None`` if the pose has too few keypoints to measure. ``offset`` is
    the exact value compared against ``HEAD_TURN_NOSE_OFFSET_RATIO`` in
    :func:`_head_turned` (horizontal nose displacement from the shoulder midpoint,
    normalized by shoulder width). ``low_confidence`` flags poses where the rule
    fires regardless of ``offset`` because landmarks are too uncertain (a strong
    look-away cue in itself).
    """
    kpts = person.keypoints
    if len(kpts) < 7:
        return None
    nose = kpts[0]
    left_eye, right_eye = kpts[1], kpts[2]
    left_shoulder, right_shoulder = kpts[5], kpts[6]
    shoulder_mid_x = (left_shoulder[0] + right_shoulder[0]) / 2
    shoulder_width = abs(right_shoulder[0] - left_shoulder[0]) or 0.1
    offset = abs(nose[0] - shoulder_mid_x) / shoulder_width
    low_confidence = (
        nose[2] < 0.3
        or left_shoulder[2] < 0.3
        or right_shoulder[2] < 0.3
        or (left_eye[2] < 0.25 and right_eye[2] < 0.25)
    )
    return {
        "offset": offset,
        "nose_conf": nose[2],
        "left_shoulder_conf": left_shoulder[2],
        "right_shoulder_conf": right_shoulder[2],
        "left_eye_conf": left_eye[2],
        "right_eye_conf": right_eye[2],
        "low_confidence": low_confidence,
    }


def _head_turned(person: PosePerson, ratio: float) -> bool:
    metrics = head_turn_offset(person)
    if metrics is None:
        return False
    # Uncertain landmarks are NOT treated as look-away — that caused constant
    # false positives (every brief pose dropout became a 5s strike episode).
    if metrics["low_confidence"]:
        return False
    return metrics["offset"] > ratio


def is_looking_away(poses: list[PosePerson], ratio: float | None = None) -> bool:
    """True if any tracked person's head is turned away this frame.

    This is a single-frame signal. The *sustained* 5-second look-away strike is
    applied by the proctoring task, which times how long this stays true across
    consecutive frames (see apps/proctoring/tasks.py). Brief glances therefore
    never produce a strike on their own.
    """
    if ratio is None:
        ratio = settings.PROCTORING.get("HEAD_TURN_NOSE_OFFSET_RATIO", 0.15)
    return any(_head_turned(person, ratio) for person in poses)


def is_gaze_off_screen(
    h_ratio: float,
    v_ratio: float,
    *,
    h_min: float | None = None,
    h_max: float | None = None,
    v_max: float | None = None,
) -> bool:
    """True when the iris position (from ml/gaze_service) is outside the
    screen-facing band. ~0.5 on both axes is a centered gaze; horizontal
    extremes mean looking left/right of the screen, a high vertical ratio
    means looking down (notes/phone in lap)."""
    cfg = settings.PROCTORING
    if h_min is None:
        h_min = cfg.get("IRIS_H_RATIO_MIN", 0.25)
    if h_max is None:
        h_max = cfg.get("IRIS_H_RATIO_MAX", 0.75)
    if v_max is None:
        v_max = cfg.get("IRIS_V_RATIO_MAX", 0.80)
    return h_ratio < h_min or h_ratio > h_max or v_ratio > v_max


def combined_looking_away(
    poses: list[PosePerson], gaze, ratio: float | None = None
) -> bool:
    """Fuse the per-frame look-away signals: head turned (pose) OR iris gaze
    off-screen. ``gaze`` is a GazeResult-like object with ``off_screen`` or
    None when gaze could not be measured this frame (which never strikes)."""
    if is_looking_away(poses, ratio):
        return True
    return bool(gaze is not None and getattr(gaze, "off_screen", False))


def evaluate_frame(
    detections: list[Detection],
    poses: list[PosePerson],
    absent_streak: int,
    multi_person_streak: int = 0,
) -> tuple[list[ViolationCandidate], int, int]:
    """Return violation candidates plus updated absent and multi-person streaks."""
    cfg = settings.PROCTORING
    candidates: list[ViolationCandidate] = []
    persons = _person_boxes(detections)
    person_count = len(persons)

    for det in detections:
        if det.class_id in PHONE_COCO_IDS:
            candidates.append(
                ViolationCandidate(
                    violation_type=ViolationLog.ViolationType.PHONE,
                    confidence=det.confidence,
                    severity=ViolationLog.Severity.HIGH,
                )
            )
        elif det.class_id in BOOK_COCO_IDS:
            candidates.append(
                ViolationCandidate(
                    violation_type=ViolationLog.ViolationType.BOOK,
                    confidence=det.confidence,
                    severity=ViolationLog.Severity.MEDIUM,
                )
            )
        elif det.class_id in SECONDARY_DEVICE_COCO_IDS and _device_near_person(
            det, persons
        ):
            candidates.append(
                ViolationCandidate(
                    violation_type=ViolationLog.ViolationType.NOTES,
                    confidence=det.confidence,
                    severity=ViolationLog.Severity.MEDIUM,
                )
            )
        # BENIGN_COCO_IDS (tv/mouse/remote) and person(0) intentionally produce
        # no violation candidate here.

    # Multiple-person rule requires persistence across consecutive frames.
    # A single frame with 2+ person boxes is frequently a false positive —
    # e.g. a raised phone occluding the body splits one person into two YOLO
    # boxes, or a face shown on the phone screen is detected as a person. A
    # real second person in the room stays visible across frames; a detection
    # glitch does not.
    min_persons = cfg.get("MULTIPLE_PERSON_MIN", 2)
    multi_person_threshold = cfg.get("MULTIPLE_PERSON_CONSECUTIVE_FRAMES", 2)
    if person_count >= min_persons:
        multi_person_streak += 1
        if multi_person_streak >= multi_person_threshold:
            max_conf = max(p.confidence for p in persons)
            candidates.append(
                ViolationCandidate(
                    violation_type=ViolationLog.ViolationType.MULTIPLE_FACES,
                    confidence=max_conf,
                    severity=ViolationLog.Severity.HIGH,
                )
            )
    else:
        multi_person_streak = 0

    absent_threshold = cfg.get("ABSENT_CONSECUTIVE_FRAMES", 2)
    if person_count == 0:
        absent_streak += 1
        if absent_streak >= absent_threshold:
            candidates.append(
                ViolationCandidate(
                    violation_type=ViolationLog.ViolationType.ABSENT,
                    confidence=0.85,
                    severity=ViolationLog.Severity.HIGH,
                )
            )
    else:
        absent_streak = 0

    # NOTE: Look-away (FACE_OBSTRUCTED) is intentionally NOT added here. It is a
    # *sustained* rule — a strike only fires after the student looks away for
    # PROCTORING['LOOK_AWAY_SECONDS'] continuously. The per-frame signal is
    # surfaced via FrameAnalysisResult.looking_away and timed in the task layer.
    return candidates, absent_streak, multi_person_streak
