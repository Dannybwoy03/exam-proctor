"""Load YOLO models once per Celery worker process."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_detector_model = None
_pose_model = None
_loaded = False
# Sticky failure marker. Without it a missing/corrupt weights file made every
# frame retry the full YOLO init (seconds of I/O per 1s frame) while
# proctoring stayed silently disabled.
_load_error: Exception | None = None


def load_models(force: bool = False) -> None:
    """Load detector and pose models into process memory.

    Failures are cached: after the first failed attempt we stop retrying
    (until ``force=True``) and ``get_detector()`` / ``get_pose_model()``
    return ``None`` immediately.
    """
    global _detector_model, _pose_model, _loaded, _load_error
    if force:
        _load_error = None
    if (_loaded or _load_error is not None) and not force:
        return

    from django.conf import settings

    cfg = settings.PROCTORING
    if cfg.get("USE_MOCK_ML"):
        _loaded = True
        logger.info("Proctoring ML: mock mode enabled (USE_MOCK_ML=true)")
        return

    device = "cpu"
    yolo_weights = cfg.get("YOLO_WEIGHTS", "yolov5n.pt")
    pose_weights = cfg.get("POSE_WEIGHTS", "yolov8n-pose.pt")

    try:
        from ultralytics import YOLO

        logger.info("Loading YOLO detector: %s", yolo_weights)
        _detector_model = YOLO(yolo_weights)
        _detector_model.to(device)

        logger.info("Loading pose model: %s", pose_weights)
        _pose_model = YOLO(pose_weights)
        _pose_model.to(device)
    except Exception as exc:  # noqa: BLE001 — any init failure disables ML
        _load_error = exc
        _detector_model = None
        _pose_model = None
        logger.critical(
            "PROCTORING ML DISABLED: failed to load YOLO models (%s / %s). "
            "AI violation detection will NOT run until this is fixed and the "
            "worker restarts (or load_models(force=True) is called).",
            yolo_weights,
            pose_weights,
            exc_info=True,
        )
        return

    _loaded = True
    logger.info("Proctoring ML models ready on %s", device)


def get_detector():
    if not _loaded and _load_error is None:
        load_models()
    return _detector_model


def get_pose_model():
    if not _loaded and _load_error is None:
        load_models()
    return _pose_model


def models_ready() -> bool:
    from django.conf import settings

    if settings.PROCTORING.get("USE_MOCK_ML"):
        return True
    return _detector_model is not None and _pose_model is not None


def load_error() -> Exception | None:
    """The cached model-load failure, if any (None when healthy)."""
    return _load_error
