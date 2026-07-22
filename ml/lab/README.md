# Model Lab

A standalone, lightweight Streamlit tool for the exam-proctor ML pipeline. It runs
the **same** detection code the server uses (`ml/yolo_service/`) so what you see
here matches production 1:1 — but with no Django server, Redis, exam flow, or
database in the way.

Use it to:

- Run YOLOv5n object detection + YOLOv8n-pose on your **live webcam**.
- See exactly **what the model sees**: bounding boxes (phone, book, person,
  laptop, keyboard) and the pose **skeleton**.
- See which **violation rules fire** each frame (phone, multiple faces, absent,
  book/notes, look-away) and the live absent-frame streak.
- **Tune thresholds** in real time (confidence, head-turn ratio, absent frames)
  and copy the resulting env vars into your run config.
- **Capture + label** frames and **fine-tune** a custom model, then load the new
  weights back into the dashboard to compare.

## Setup

```bash
source .venv/bin/activate
pip install -r ml/lab/requirements-lab.txt
```

(`torch`, `ultralytics`, `opencv-python`, and `numpy` are already installed via the
project's main `requirements.txt`.)

## Run the dashboard

From the project root:

```bash
streamlit run ml/lab/app.py
```

Then click **Start camera** in the sidebar. Hold up a phone or turn your head and
watch the **Fired violations** panel.

> macOS will prompt for camera permission the first time. If the webcam doesn't
> open, make sure no other app (Zoom, browser tab) is holding the camera.

## Capture data for training

In the dashboard, open the **Capture** section:

1. Hold the object/pose you want to teach (e.g. a phone).
2. The lab pre-fills boxes from the current model (auto-label assist). Pick the
   correct class for each box you want to keep, or drop wrong ones.
3. Click **Save frame + labels**. Images and YOLO-format labels are written to
   `ml/lab/dataset/`.

For manual correction or richer labeling, the YOLO `.txt` files are compatible
with [LabelImg](https://github.com/HumanSignal/labelImg) and Roboflow.

## Fine-tune a custom model

Once you have captured a set (a few hundred frames per class is a reasonable
start):

```bash
python ml/lab/train.py --epochs 50 --imgsz 416
```

This writes `ml/lab/dataset/data.yaml` and runs Ultralytics training on CPU. The
best weights land under `runs/detect/train*/weights/best.pt`. Point the dashboard
at them with the **Weights** selector in the sidebar (or paste the path) to
compare before/after.

## Notes

- **Object infractions** (phone, book, notes/laptop) are real YOLO classes, so
  fine-tuning improves recall in your lighting/camera.
- **"Looking away"** is a pose heuristic, not an object class — tune it with the
  `Head-turn ratio` slider; it is shown live in the violations panel.
- `ml/lab/dataset/` and `runs/` are git-ignored.
