"""Load the InsightFace FaceAnalysis model once per process.

Mirrors ml/gaze_service/loader.py: failures are sticky so a broken install
never retries the full model init on every request. When the model is
unavailable the caller degrades gracefully (registration saves the photo
without an embedding; exam-time verify auto-passes like the old
face_recognition fallback did).

Uses the ``buffalo_l`` model pack (SCRFD face detection + ArcFace
recognition, 512-dim embeddings). The pack (~280MB) auto-downloads to
``~/.insightface`` on first use.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_analyzer = None
_loaded = False
_load_error: Exception | None = None


def load_face_analyzer(force: bool = False) -> None:
    """Initialise the InsightFace FaceAnalysis app (detection + recognition)."""
    global _analyzer, _loaded, _load_error
    if force:
        _load_error = None
    if (_loaded or _load_error is not None) and not force:
        return

    from django.conf import settings

    cfg = settings.PROCTORING
    if cfg.get("USE_MOCK_ML"):
        _loaded = True
        logger.info("Face ID: disabled (mock ML mode)")
        return

    try:
        from insightface.app import FaceAnalysis

        analyzer = FaceAnalysis(
            name="buffalo_l",
            allowed_modules=["detection", "recognition"],
            providers=["CPUExecutionProvider"],
        )
        # det_size trades accuracy for speed; 640 is the insightface default.
        analyzer.prepare(ctx_id=-1, det_size=(640, 640))
        _analyzer = analyzer
    except Exception as exc:  # noqa: BLE001 — any init failure disables face ID
        _load_error = exc
        _analyzer = None
        logger.warning(
            "Face ID disabled: could not initialise InsightFace (buffalo_l). "
            "Registration face scans are stored without embeddings and the "
            "exam-time face match is skipped. Install insightface + "
            "onnxruntime, then restart.",
            exc_info=True,
        )
        return

    _loaded = True
    logger.info("Face ID: InsightFace buffalo_l ready (CPU)")


def get_face_analyzer():
    if not _loaded and _load_error is None:
        load_face_analyzer()
    return _analyzer


def face_id_ready() -> bool:
    return get_face_analyzer() is not None


def load_error() -> Exception | None:
    return _load_error
