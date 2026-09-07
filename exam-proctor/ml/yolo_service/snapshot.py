"""Persist violation snapshots with bbox + pose metadata."""

from __future__ import annotations

import uuid
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile

from apps.proctoring.models import ViolationLog, ViolationSnapshot

from .detector import Detection
from .pipeline import FrameAnalysisResult
from .pose import PosePerson


def _native_float(value) -> float:
    """JSONField / Channels cannot serialize numpy scalar types."""
    return float(value)


def _detections_to_json(detections: list[Detection]) -> list[dict]:
    return [
        {
            "label": d.label,
            "class_id": int(d.class_id),
            "x": _native_float(d.x),
            "y": _native_float(d.y),
            "w": _native_float(d.w),
            "h": _native_float(d.h),
            "confidence": _native_float(d.confidence),
        }
        for d in detections
    ]


def _poses_to_json(poses: list[PosePerson]) -> list[dict]:
    return [
        {
            "person_index": int(p.person_index),
            "keypoints": [
                [_native_float(pt[0]), _native_float(pt[1]), _native_float(pt[2])]
                for pt in p.keypoints
            ],
        }
        for p in poses
    ]


def _encode_jpeg(analysis: FrameAnalysisResult, quality: int) -> bytes:
    """Re-encode the frame as JPEG at the configured quality; fall back to the
    original bytes if encoding fails so a snapshot is never lost entirely."""
    import cv2

    try:
        ok, buf = cv2.imencode(
            ".jpg", analysis.image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
        )
        if ok:
            return buf.tobytes()
    except Exception:
        pass
    return analysis.frame_bytes


def create_violation_snapshot(
    violation: ViolationLog,
    analysis: FrameAnalysisResult,
) -> ViolationSnapshot:
    quality = settings.PROCTORING.get("SNAPSHOT_JPEG_QUALITY", 72)
    filename = f"violation_{violation.pk}_{uuid.uuid4().hex[:8]}.jpg"

    gaze_metrics = {}
    if analysis.gaze_h_ratio is not None and analysis.gaze_v_ratio is not None:
        gaze_metrics = {
            "h_ratio": round(_native_float(analysis.gaze_h_ratio), 4),
            "v_ratio": round(_native_float(analysis.gaze_v_ratio), 4),
            "off_screen": bool(analysis.gaze_off_screen),
        }

    snapshot, _ = ViolationSnapshot.objects.update_or_create(
        violation=violation,
        defaults={
            "bounding_boxes": _detections_to_json(analysis.detections),
            "pose_keypoints": _poses_to_json(analysis.poses),
            "gaze_metrics": gaze_metrics,
            "frame_width": analysis.frame_width,
            "frame_height": analysis.frame_height,
        },
    )
    if not snapshot.image:
        snapshot.image.save(
            filename,
            ContentFile(_encode_jpeg(analysis, quality)),
            save=False,
        )
        snapshot.save(update_fields=["image"])
    return snapshot
