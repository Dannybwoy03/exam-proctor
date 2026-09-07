"""YOLOv5n object detection for proctoring violations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Single source of truth for the COCO classes the proctor reports, in display
# order. yolov5n is COCO-pretrained, so these ids are fixed by the base model.
#   person (0)      - presence / absent / multiple-person rules
#   tv (62)         - second screen / monitor (contextual, no strike by default)
#   laptop (63)     - secondary device -> notes rule when near a person
#   mouse (64)      - benign desk object (kept so it isn't misread as a phone)
#   remote (65)     - phone-confusable; reported so it shows as "remote", not "phone"
#   keyboard (66)   - secondary device -> notes rule when near a person
#   cell phone (67) - phone violation
#   book (73)       - book / notes violation
COCO_NAMES = {
    0: "person",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    66: "keyboard",
    67: "cell phone",
    73: "book",
}

# Default set of COCO ids YOLOv5 is allowed to report. settings.PROCTORING
# ["YOLO_CLASSES"] overrides this; keep the two in sync.
DEFAULT_PROCTOR_CLASS_IDS = list(COCO_NAMES)


@dataclass
class Detection:
    class_id: int
    label: str
    confidence: float
    x: float
    y: float
    w: float
    h: float


def _normalize_box(xyxy, img_w: int, img_h: int) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = (float(v) for v in xyxy)
    img_w = float(img_w) or 1.0
    img_h = float(img_h) or 1.0
    w = max(0.0, (x2 - x1) / img_w)
    h = max(0.0, (y2 - y1) / img_h)
    x = max(0.0, x1 / img_w)
    y = max(0.0, y1 / img_h)
    return float(x), float(y), float(w), float(h)


def run_detection(image_bgr: np.ndarray) -> list[Detection]:
    from django.conf import settings

    cfg = settings.PROCTORING
    if cfg.get("USE_MOCK_ML"):
        return []

    from ml.yolo_service.loader import get_detector

    model = get_detector()
    if model is None:
        return []

    img_h, img_w = image_bgr.shape[:2]
    allowed = set(cfg.get("YOLO_CLASSES", DEFAULT_PROCTOR_CLASS_IDS))
    conf = cfg.get("YOLO_CONFIDENCE", 0.40)
    imgsz = cfg.get("YOLO_IMG_SIZE", 416)

    results = model.predict(
        source=image_bgr,
        imgsz=imgsz,
        conf=conf,
        device="cpu",
        verbose=False,
        classes=list(allowed),
    )

    detections: list[Detection] = []
    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue
        for box in boxes:
            cls_id = int(box.cls.item())
            if cls_id not in allowed:
                continue
            xyxy = box.xyxy[0].cpu().numpy()
            x, y, w, h = _normalize_box(xyxy, img_w, img_h)
            detections.append(
                Detection(
                    class_id=cls_id,
                    label=COCO_NAMES.get(cls_id, result.names.get(cls_id, str(cls_id))),
                    confidence=float(box.conf.item()),
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                )
            )
    return detections
