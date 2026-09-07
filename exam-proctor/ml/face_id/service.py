"""Embed and compare faces with InsightFace (ArcFace, 512-dim embeddings).

``embed_face`` returns the normalized embedding of the largest face in the
image, or ``None`` when no face is found (or the image cannot be decoded).
Callers that need to distinguish "no face" from "model not installed" should
check ``face_id_available()`` first.

``match_score`` is the cosine similarity of two embeddings, in [-1, 1] but
practically [0, 1] for face pairs. Same-person pairs typically score >= 0.5;
different people < 0.2. The pass threshold lives in
``settings.PROCTORING["FACE_ID_MATCH_THRESHOLD"]``.
"""

from __future__ import annotations

import logging

from .loader import face_id_ready, get_face_analyzer

logger = logging.getLogger(__name__)


def face_id_available() -> bool:
    """True when the InsightFace model is loaded and usable."""
    return face_id_ready()


def _decode_bgr(image_bytes: bytes):
    import cv2
    import numpy as np

    buf = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)  # None on bad data


def embed_face(image_bytes: bytes) -> list[float] | None:
    """Normalized 512-dim embedding of the largest face, or None if no face."""
    analyzer = get_face_analyzer()
    if analyzer is None:
        return None

    img = _decode_bgr(image_bytes)
    if img is None:
        logger.warning("Face ID: could not decode image (%d bytes)", len(image_bytes))
        return None

    faces = analyzer.get(img)
    if not faces:
        return None

    def _area(face):
        x1, y1, x2, y2 = face.bbox
        return max(0.0, float(x2 - x1)) * max(0.0, float(y2 - y1))

    face = max(faces, key=_area)
    embedding = getattr(face, "normed_embedding", None)
    if embedding is None:
        return None
    return [float(v) for v in embedding]


def match_score(embedding_a: list[float], embedding_b: list[float]) -> float:
    """Cosine similarity between two embeddings (re-normalized for safety)."""
    import numpy as np

    a = np.asarray(embedding_a, dtype=np.float32)
    b = np.asarray(embedding_b, dtype=np.float32)
    norm = float(np.linalg.norm(a)) * float(np.linalg.norm(b))
    if norm == 0.0:
        return 0.0
    return float(np.dot(a, b) / norm)
