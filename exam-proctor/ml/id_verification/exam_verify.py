"""Exam-time face verification against the registration face embedding.

Uses ml/face_id (InsightFace/ArcFace). The reference embedding is captured
by the live face scan at registration and stored in
``StudentProfile.face_embedding``. Accounts that predate the scan are lazily
backfilled from their profile photo or ID card upload on the first check.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExamVerifyResult:
    passed: bool
    id_confidence: float
    face_match_score: float
    errors: list[str]


def _reference_photo_bytes(student_profile, user) -> bytes | None:
    """Best available face reference image: profile photo, then ID card scan."""
    for field in (user.profile_photo, getattr(student_profile, "id_proof_image", None)):
        if field:
            with field.open("rb") as handle:
                return handle.read()
    return None


def _reference_embedding(student_profile, user) -> list[float] | None:
    """Stored embedding, or lazy backfill from the reference photo."""
    from ml.face_id.service import embed_face

    stored = student_profile.face_embedding
    if stored:
        return stored

    photo_bytes = _reference_photo_bytes(student_profile, user)
    if photo_bytes is None:
        return None

    embedding = embed_face(photo_bytes)
    if embedding is None:
        return None

    student_profile.face_embedding = embedding
    student_profile.save(update_fields=["face_embedding"])
    return embedding


def verify_exam_id_frame(frame_bytes, *, student_profile) -> ExamVerifyResult:
    """Verify the webcam frame face matches the registration face embedding."""
    user = student_profile.user

    try:
        from django.conf import settings

        from ml.face_id.service import embed_face, face_id_available, match_score

        if not face_id_available():
            # Model not installed / mock mode — allow the attempt so students
            # aren't stuck on VERIFYING forever (teachers still get ML proctoring).
            return ExamVerifyResult(
                passed=True,
                id_confidence=0.5,
                face_match_score=0.5,
                errors=["Face ID model unavailable; face match skipped."],
            )

        reference = _reference_embedding(student_profile, user)
        if reference is None:
            if _reference_photo_bytes(student_profile, user) is None:
                # No scan or photo on file at all — cannot match; allow the
                # attempt rather than blocking the exam.
                return ExamVerifyResult(
                    passed=True,
                    id_confidence=0.0,
                    face_match_score=0.0,
                    errors=["No face scan or photo on file; face match skipped."],
                )
            return ExamVerifyResult(
                passed=False,
                id_confidence=0.0,
                face_match_score=0.0,
                errors=["Could not read a face from the registration photo."],
            )

        frame_embedding = embed_face(frame_bytes)
        if frame_embedding is None:
            return ExamVerifyResult(
                passed=False,
                id_confidence=0.0,
                face_match_score=0.0,
                errors=["No face detected in webcam frame."],
            )

        threshold = settings.PROCTORING.get("FACE_ID_MATCH_THRESHOLD", 0.35)
        score = match_score(reference, frame_embedding)
        passed = score >= threshold

        return ExamVerifyResult(
            passed=passed,
            id_confidence=0.9 if passed else 0.4,
            face_match_score=score,
            errors=[] if passed else [f"Face match score {score:.2f} below threshold."],
        )
    except Exception as exc:  # noqa: BLE001 — verification must never crash the task
        return ExamVerifyResult(
            passed=False,
            id_confidence=0.0,
            face_match_score=0.0,
            errors=[f"Face verification error: {exc}"],
        )
