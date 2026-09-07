"""Face identity verification (InsightFace/ArcFace).

Separate from the exam proctoring pipeline (ml/yolo_service, ml/gaze_service).
Used for:
- Registration: embed the live webcam face scan into StudentProfile.face_embedding
- Pre-exam identity check: compare a webcam frame against the stored embedding
"""
