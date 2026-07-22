"""YOLOv8n-pose inference for skeleton overlays."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# COCO-17 skeleton edges for UI rendering.
SKELETON_EDGES = [
    (0, 1),
    (0, 2),
    (1, 3),
    (2, 4),
    (5, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
]


@dataclass
class PosePerson:
    person_index: int
    keypoints: list[list[float]]


def run_pose(image_bgr: np.ndarray) -> list[PosePerson]:
    from django.conf import settings

    cfg = settings.PROCTORING
    if cfg.get("USE_MOCK_ML"):
        return []

    from ml.yolo_service.loader import get_pose_model

    model = get_pose_model()
    if model is None:
        return []

    img_h, img_w = image_bgr.shape[:2]
    conf = cfg.get("POSE_CONFIDENCE", 0.50)
    imgsz = cfg.get("YOLO_IMG_SIZE", 416)

    results = model.predict(
        source=image_bgr,
        imgsz=imgsz,
        conf=conf,
        device="cpu",
        verbose=False,
    )

    people: list[PosePerson] = []
    for result in results:
        if result.keypoints is None:
            continue
        kpts_data = result.keypoints.data
        if kpts_data is None:
            continue
        for idx, person_kpts in enumerate(kpts_data.cpu().numpy()):
            normalized = []
            for pt in person_kpts:
                # Guard malformed keypoint rows so one bad tensor doesn't
                # abort analysis of the whole frame.
                if len(pt) < 3:
                    continue
                x, y, c = pt[0], pt[1], pt[2]
                normalized.append(
                    [
                        float(x / img_w) if img_w else 0.0,
                        float(y / img_h) if img_h else 0.0,
                        float(c),
                    ]
                )
            if normalized:
                people.append(PosePerson(person_index=idx, keypoints=normalized))
    return people
