"""Fine-tune a custom infraction detector from frames captured in the Model Lab.

Usage (from project root, venv active):

    python ml/lab/train.py --epochs 50 --imgsz 416

Outputs the best weights under ``runs/detect/<name>/weights/best.pt``. Point the
dashboard's "Weights" selector at that file to compare against the base model.
"""

from __future__ import annotations

import argparse
import sys

# Allow running both as a script (``python ml/lab/train.py``) and as a module.
if __package__ in (None, ""):
    from bootstrap import setup_django
else:
    from .bootstrap import setup_django


def main() -> int:
    setup_django()

    from ml.lab.capture import LAB_CLASSES, count_samples, write_data_yaml

    parser = argparse.ArgumentParser(description="Fine-tune the lab infraction detector.")
    parser.add_argument(
        "--base",
        default="yolov5nu.pt",
        help="Base weights to fine-tune from (default: yolov5nu.pt).",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu", help="cpu / mps / 0 (CUDA).")
    parser.add_argument("--name", default="lab_infractions", help="Run name under runs/detect/.")
    args = parser.parse_args()

    n = count_samples()
    if n == 0:
        print(
            "No captured samples found in ml/lab/dataset/images/.\n"
            "Open the dashboard (streamlit run ml/lab/app.py) and capture frames "
            "first."
        )
        return 1

    data_yaml = write_data_yaml()
    print(f"Dataset: {n} image(s), classes={LAB_CLASSES}")
    print(f"Wrote {data_yaml}")
    print(f"Fine-tuning {args.base} for {args.epochs} epoch(s) on {args.device} ...")

    from ultralytics import YOLO

    model = YOLO(args.base)
    results = model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        name=args.name,
        exist_ok=True,
        verbose=True,
    )

    save_dir = getattr(results, "save_dir", None)
    if save_dir:
        print(f"\nDone. Best weights: {save_dir}/weights/best.pt")
        print("Load it in the dashboard via the Weights selector to compare.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
