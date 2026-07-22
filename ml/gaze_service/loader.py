"""Load the MediaPipe FaceLandmarker (iris) model once per Celery worker process.

Mirrors ml/yolo_service/loader.py: failures are sticky so a broken install
never retries the full model init on every 1s frame, and a dead gaze model
degrades the pipeline to pose-only look-away instead of erroring frames.

Uses the MediaPipe Tasks API (mediapipe>=0.10.x removed the legacy
``mp.solutions`` interface). Requires the ``face_landmarker.task`` model
asset, which outputs 478 landmarks including the iris points.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_landmarker = None
_loaded = False
_load_error: Exception | None = None


def load_gaze_model(force: bool = False) -> None:
    """Initialise the FaceLandmarker with iris landmarks."""
    global _landmarker, _loaded, _load_error
    if force:
        _load_error = None
    if (_loaded or _load_error is not None) and not force:
        return

    from django.conf import settings

    cfg = settings.PROCTORING
    if cfg.get("USE_MOCK_ML") or not cfg.get("USE_IRIS_GAZE", True):
        _loaded = True
        logger.info("Iris gaze: disabled (mock mode or USE_IRIS_GAZE=false)")
        return

    model_path = cfg.get("FACE_LANDMARKER_MODEL", "face_landmarker.task")

    try:
        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision

        options = vision.FaceLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
        )
        _landmarker = vision.FaceLandmarker.create_from_options(options)
    except Exception as exc:  # noqa: BLE001 — any init failure disables gaze
        _load_error = exc
        _landmarker = None
        logger.warning(
            "Iris gaze disabled: could not initialise MediaPipe FaceLandmarker "
            "(model: %s). Look-away detection falls back to head pose only. "
            "Install mediapipe and download face_landmarker.task, then restart "
            "the worker.",
            model_path,
            exc_info=True,
        )
        return

    _loaded = True
    logger.info("Iris gaze: MediaPipe FaceLandmarker ready (%s)", model_path)


def get_landmarker():
    if not _loaded and _load_error is None:
        load_gaze_model()
    return _landmarker


def gaze_ready() -> bool:
    return _landmarker is not None


def load_error() -> Exception | None:
    return _load_error
