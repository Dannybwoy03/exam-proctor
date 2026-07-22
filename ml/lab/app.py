"""Model Lab - Streamlit dashboard.

Runs the project's real proctoring pipeline (ml/yolo_service) on a live webcam so
you can see detections, the pose skeleton, and exactly which violation rules fire,
tune thresholds live, and capture/label frames for fine-tuning.

Run from the project root:  streamlit run ml/lab/app.py
"""

from __future__ import annotations

import cv2
import streamlit as st

# --- Django + path bootstrap (must run before importing ml.yolo_service) ----
if __package__ in (None, ""):
    from bootstrap import PROJECT_ROOT, setup_django
else:
    from .bootstrap import PROJECT_ROOT, setup_django

setup_django()

from django.conf import settings  # noqa: E402

from apps.proctoring.models import ViolationLog  # noqa: E402
from ml.lab import capture as cap_mod  # noqa: E402
from ml.lab import viz  # noqa: E402
from ml.yolo_service.loader import load_models  # noqa: E402
from ml.yolo_service.pipeline import analyze_frame  # noqa: E402
from ml.yolo_service.pose import run_pose  # noqa: E402
from ml.yolo_service.rules import head_turn_offset  # noqa: E402

# Sliders write into this in-process dict; the pipeline reads from it per frame.
PROCTORING = settings.PROCTORING

VIOLATION_LABELS = {vt.value: vt.label for vt in ViolationLog.ViolationType}


# --------------------------------------------------------------------------- #
# Camera helpers (kept in session_state so it survives Streamlit reruns)
# --------------------------------------------------------------------------- #
def get_capture(index: int):
    cap = st.session_state.get("cap")
    if cap is not None and st.session_state.get("cap_index") == index and cap.isOpened():
        return cap
    release_capture()
    cap = cv2.VideoCapture(index)
    st.session_state["cap"] = cap
    st.session_state["cap_index"] = index
    return cap


def release_capture():
    cap = st.session_state.get("cap")
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    st.session_state["cap"] = None


def discover_weights() -> list[str]:
    """Find fine-tuned weights produced by train.py."""
    found = []
    runs = PROJECT_ROOT / "runs" / "detect"
    if runs.exists():
        for pt in sorted(runs.glob("*/weights/best.pt")):
            found.append(str(pt))
    return found


def apply_weights(selected: str):
    """Swap the detector weights if the selection changed (forces a reload)."""
    if st.session_state.get("active_weights") == selected:
        return
    PROCTORING["YOLO_WEIGHTS"] = selected
    with st.spinner(f"Loading weights: {selected} ..."):
        load_models(force=True)
    st.session_state["active_weights"] = selected


# --------------------------------------------------------------------------- #
# Page
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Proctor Model Lab", layout="wide")
st.title("Proctor Model Lab")
st.caption(
    "Live YOLOv5n + YOLOv8n-pose on your webcam, running the same pipeline the "
    "exam server uses. Tune thresholds, watch which rules fire, capture and label "
    "frames to fine-tune."
)

if PROCTORING.get("USE_MOCK_ML"):
    st.error(
        "PROCTORING_USE_MOCK_ML is true, so the model returns nothing. Unset it "
        "(`unset PROCTORING_USE_MOCK_ML`) and restart the lab to run the real model."
    )

# session defaults
st.session_state.setdefault("absent_streak", 0)
st.session_state.setdefault("multi_person_streak", 0)
st.session_state.setdefault("last_frame", None)
st.session_state.setdefault("last_detections", [])
st.session_state.setdefault(
    "head_ratio", float(PROCTORING.get("HEAD_TURN_NOSE_OFFSET_RATIO", 0.15))
)
base_weights = PROCTORING.get("YOLO_WEIGHTS", "yolov5nu.pt")
st.session_state.setdefault("active_weights", base_weights)

# --------------------------------------------------------------------------- #
# Sidebar controls
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Camera")
    cam_index = st.number_input("Camera index", min_value=0, max_value=8, value=0, step=1)
    live = st.checkbox("Start camera", value=False, key="live")
    fps_cap = st.slider("Max FPS", 1, 15, 6, help="Caps CPU usage of the live loop.")

    st.header("Model weights")
    weight_options = [base_weights] + [w for w in discover_weights() if w != base_weights]
    labels = ["Base: " + base_weights] + [
        "Fine-tuned: " + w.split("runs/")[-1] for w in weight_options[1:]
    ]
    choice = st.selectbox("Detector weights", options=list(range(len(weight_options))),
                          format_func=lambda i: labels[i])
    selected_weights = weight_options[choice]
    custom = st.text_input("...or custom weights path", value="")
    if custom.strip():
        selected_weights = custom.strip()

    st.header("Thresholds (live)")
    yolo_conf = st.slider("YOLO confidence", 0.05, 0.95,
                          float(PROCTORING.get("YOLO_CONFIDENCE", 0.40)), 0.01)
    pose_conf = st.slider("Pose confidence", 0.05, 0.95,
                          float(PROCTORING.get("POSE_CONFIDENCE", 0.50)), 0.01)
    imgsz = st.select_slider("Inference image size", options=[320, 384, 416, 512, 640],
                             value=int(PROCTORING.get("YOLO_IMG_SIZE", 416)))
    head_ratio = st.slider("Head-turn ratio (look-away)", 0.05, 0.60,
                           step=0.01, key="head_ratio")
    absent_frames = st.slider("Absent consecutive frames", 1, 10,
                              int(PROCTORING.get("ABSENT_CONSECUTIVE_FRAMES", 2)))
    multi_min = st.slider("Multiple-person minimum", 2, 5,
                          int(PROCTORING.get("MULTIPLE_PERSON_MIN", 2)))

    st.header("Iris gaze (look-away)")
    use_iris = st.checkbox("Enable iris gaze", value=bool(PROCTORING.get("USE_IRIS_GAZE", True)))
    iris_h_min = st.slider("Gaze H min (left bound)", 0.0, 0.5,
                           float(PROCTORING.get("IRIS_H_RATIO_MIN", 0.25)), 0.01)
    iris_h_max = st.slider("Gaze H max (right bound)", 0.5, 1.0,
                           float(PROCTORING.get("IRIS_H_RATIO_MAX", 0.75)), 0.01)
    iris_v_max = st.slider("Gaze V max (down bound)", 0.5, 1.5,
                           float(PROCTORING.get("IRIS_V_RATIO_MAX", 0.80)), 0.01)

    st.header("Overlays")
    show_boxes = st.checkbox("Boxes", value=True)
    show_labels = st.checkbox("Box labels", value=True)
    show_skeleton = st.checkbox("Skeleton", value=True)

# Push slider values into the live config so the pipeline picks them up.
PROCTORING["YOLO_CONFIDENCE"] = yolo_conf
PROCTORING["POSE_CONFIDENCE"] = pose_conf
PROCTORING["YOLO_IMG_SIZE"] = int(imgsz)
PROCTORING["HEAD_TURN_NOSE_OFFSET_RATIO"] = head_ratio
PROCTORING["ABSENT_CONSECUTIVE_FRAMES"] = int(absent_frames)
PROCTORING["MULTIPLE_PERSON_MIN"] = int(multi_min)
PROCTORING["USE_IRIS_GAZE"] = bool(use_iris)
PROCTORING["IRIS_H_RATIO_MIN"] = float(iris_h_min)
PROCTORING["IRIS_H_RATIO_MAX"] = float(iris_h_max)
PROCTORING["IRIS_V_RATIO_MAX"] = float(iris_v_max)

apply_weights(selected_weights)

# --------------------------------------------------------------------------- #
# Frame processing + rendering
# --------------------------------------------------------------------------- #
def render_live(result):
    """Render video + info panels for one frame. Called inside the fragment, so
    only this region redraws each tick (no full-page flashing)."""
    video_col, info_col = st.columns([3, 2])

    overlaid = viz.draw_overlays(
        result.image_bgr,
        result.detections,
        result.poses,
        show_boxes=show_boxes,
        show_skeleton=show_skeleton,
        show_labels=show_labels,
    )
    video_col.image(viz.to_rgb(overlaid), channels="RGB", use_container_width=True)

    person_count = sum(1 for d in result.detections if d.class_id == 0)
    m1, m2, m3 = info_col.columns(3)
    m1.metric("Inference", f"{result.inference_ms:.0f} ms")
    m2.metric("People", person_count)
    m3.metric("Absent streak", f"{result.absent_streak}/{absent_frames}")

    if use_iris:
        g1, g2, g3 = info_col.columns(3)
        if result.gaze_h_ratio is not None:
            g1.metric("Gaze H", f"{result.gaze_h_ratio:.2f}")
            g2.metric("Gaze V", f"{result.gaze_v_ratio:.2f}")
            g3.metric("Gaze", "OFF-SCREEN" if result.gaze_off_screen else "on-screen")
        else:
            g1.metric("Gaze H", "—")
            g2.metric("Gaze V", "—")
            g3.metric("Gaze", "no face")
    if result.looking_away:
        info_col.warning("Looking away this frame (head turn or gaze).")

    info_col.markdown("**Fired violations**")
    if result.violations:
        for v in result.violations:
            name = VIOLATION_LABELS.get(v.violation_type, v.violation_type)
            info_col.warning(f"{name}  -  severity {v.severity}, conf {v.confidence:.2f}")
    else:
        info_col.info("No violations this frame.")

    info_col.markdown("**Detections**")
    if result.detections:
        info_col.dataframe(
            [
                {
                    "class": d.label,
                    "conf": round(d.confidence, 3),
                    "x": round(d.x, 3),
                    "y": round(d.y, 3),
                    "w": round(d.w, 3),
                    "h": round(d.h, 3),
                }
                for d in result.detections
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        info_col.write("none")


def render_static():
    """Static view when the camera is stopped (rendered once, no auto-rerun)."""
    video_col, info_col = st.columns([3, 2])
    last = st.session_state.get("last_frame")
    if last is not None:
        overlaid = viz.draw_overlays(
            last,
            st.session_state.get("last_detections", []),
            [],
            show_boxes=show_boxes,
            show_skeleton=False,
            show_labels=show_labels,
        )
        video_col.image(viz.to_rgb(overlaid), channels="RGB", use_container_width=True)
        info_col.info("Camera stopped. Showing last captured frame.")
    else:
        video_col.info("Click **Start camera** in the sidebar to begin.")


def process_one_frame(frame_bgr):
    ok, buf = cv2.imencode(".jpg", frame_bgr)
    if not ok:
        return None
    result = analyze_frame(
        buf.tobytes(),
        absent_streak=st.session_state["absent_streak"],
        multi_person_streak=st.session_state["multi_person_streak"],
    )
    if result is None:
        return None
    st.session_state["absent_streak"] = result.absent_streak
    st.session_state["multi_person_streak"] = result.multi_person_streak
    st.session_state["last_frame"] = result.image_bgr
    st.session_state["last_detections"] = result.detections
    return result


def live_view():
    """Grab and render one frame. Wrapped in st.fragment so it reruns on a timer
    without re-running the whole page."""
    cap = get_capture(int(cam_index))
    if not cap.isOpened():
        st.error(f"Could not open camera index {cam_index}. Close other apps using it.")
        return
    ok, frame = cap.read()
    if not ok or frame is None:
        st.warning("Waiting for camera frame...")
        return
    result = process_one_frame(frame)
    if result is not None:
        render_live(result)


# --------------------------------------------------------------------------- #
# Live stream: ONLY the video fragment reruns on a timer, so the rest of the
# page stays put and there is no full-page flashing.
# --------------------------------------------------------------------------- #
if live:
    fps_interval = 1.0 / float(fps_cap)
    live_fragment = st.fragment(run_every=fps_interval)(live_view)
    live_fragment()
else:
    release_capture()
    st.session_state["absent_streak"] = 0
    st.session_state["multi_person_streak"] = 0
    render_static()

# --------------------------------------------------------------------------- #
# Capture & labeling
# --------------------------------------------------------------------------- #
st.divider()
st.subheader("Capture data for fine-tuning")
st.caption(
    f"Saved samples so far: {cap_mod.count_samples()}  ->  {cap_mod.dataset_root()}"
)

cap_col1, cap_col2 = st.columns(2)

with cap_col1:
    st.markdown("**Quick capture** (saves the current frame with auto-labels)")
    if st.button("Quick-capture frame", disabled=st.session_state.get("last_frame") is None):
        frame = st.session_state["last_frame"]
        cands = cap_mod.detections_to_label_candidates(
            st.session_state.get("last_detections", [])
        )
        path = cap_mod.save_sample(frame, cands)
        st.success(f"Saved {path.name} with {len(cands)} label(s).")

with cap_col2:
    st.markdown("**Manual label & save** (stop the camera first)")
    if live:
        st.caption("Uncheck *Start camera* to label frames precisely.")
    elif st.session_state.get("last_frame") is None:
        st.caption("No frame captured yet.")
    else:
        cands = cap_mod.detections_to_label_candidates(
            st.session_state.get("last_detections", [])
        )
        if not cands:
            st.caption(
                "Model found no labelable objects. You can still save this as a "
                "negative/background sample below."
            )
        chosen: list[cap_mod.LabelCandidate] = []
        for i, c in enumerate(cands):
            cols = st.columns([1, 2, 2])
            include = cols[0].checkbox("keep", value=True, key=f"keep_{i}")
            cls_idx = cols[1].selectbox(
                "class",
                options=list(range(len(cap_mod.LAB_CLASSES))),
                index=c.lab_index,
                format_func=lambda j: cap_mod.LAB_CLASSES[j],
                key=f"cls_{i}",
            )
            cols[2].caption(f"conf {c.confidence:.2f}")
            if include:
                c.lab_index = cls_idx
                c.label = cap_mod.LAB_CLASSES[cls_idx]
                chosen.append(c)
        if st.button("Save frame + labels"):
            path = cap_mod.save_sample(st.session_state["last_frame"], chosen)
            st.success(f"Saved {path.name} with {len(chosen)} label(s).")

with st.expander("How to fine-tune on what you've captured"):
    st.code(
        "source .venv/bin/activate\n"
        "python ml/lab/train.py --epochs 50 --imgsz 416\n"
        "# then pick runs/detect/lab_infractions/weights/best.pt in the sidebar",
        language="bash",
    )

# --------------------------------------------------------------------------- #
# Look-away calibration
# --------------------------------------------------------------------------- #
st.divider()
st.subheader("Look-away calibration")
st.caption(
    "\"Looking away\" is detected from pose geometry, not an object class. Strike a "
    "look-away pose, measure its head-turn offset on the current frame, then set "
    "the threshold so this pose (and anything more turned) trips the rule."
)


def _calibrate_lookaway():
    """Button callback: set the live head-turn threshold from the measured pose.
    Runs before the rerun, so writing the widget's session_state key is safe."""
    off = st.session_state.get("lookaway_offset")
    if off is None:
        return
    margin = float(st.session_state.get("lookaway_margin", 0.03))
    st.session_state["head_ratio"] = round(max(0.05, off - margin), 3)
    st.session_state["lookaway_calibrated"] = st.session_state["head_ratio"]


def _measure_lookaway(frame_bgr):
    """Pick the most confident person and measure their head-turn offset."""
    poses = run_pose(frame_bgr)
    best = None
    for person in poses:
        m = head_turn_offset(person)
        if m is None:
            continue
        if best is None or m["nose_conf"] > best["nose_conf"]:
            best = m
    return best, len(poses)


cal_frame = st.session_state.get("last_frame")
col_a, col_b = st.columns([1, 2])

with col_a:
    if st.button("Measure look-away on current frame", disabled=cal_frame is None):
        metrics, n_people = _measure_lookaway(cal_frame)
        st.session_state["lookaway_metrics"] = metrics
        st.session_state["lookaway_offset"] = metrics["offset"] if metrics else None
        st.session_state["lookaway_people"] = n_people
    if cal_frame is None:
        st.caption("Start the camera (or capture a frame) first.")

with col_b:
    metrics = st.session_state.get("lookaway_metrics")
    if metrics is None:
        if "lookaway_offset" in st.session_state and st.session_state.get("lookaway_people", 0) == 0:
            st.warning("No measurable pose found in that frame. Make sure your head and shoulders are visible.")
    else:
        offset = metrics["offset"]
        fires_now = metrics["low_confidence"] or offset > head_ratio
        st.metric("Measured head-turn offset", f"{offset:.3f}")
        st.write(
            f"Current threshold: **{head_ratio:.3f}**  |  "
            f"This pose currently fires look-away: **{'YES' if fires_now else 'NO'}**"
        )
        if metrics["low_confidence"]:
            st.info(
                "Landmarks are low-confidence on this frame (head turned far enough "
                "that the model is unsure) - this already trips look-away on its own."
            )
        st.caption(
            f"nose conf {metrics['nose_conf']:.2f}, shoulders "
            f"{metrics['left_shoulder_conf']:.2f}/{metrics['right_shoulder_conf']:.2f}"
        )
        st.number_input(
            "Safety margin (set threshold this much below the measurement)",
            min_value=0.0, max_value=0.20, value=0.03, step=0.01, key="lookaway_margin",
        )
        st.button(
            "Calibrate threshold to this pose",
            on_click=_calibrate_lookaway,
            disabled=st.session_state.get("lookaway_offset") is None,
        )

if "lookaway_calibrated" in st.session_state:
    st.success(
        f"Look-away threshold calibrated to {st.session_state['lookaway_calibrated']:.3f}. "
        "To make this permanent, set HEAD_TURN_NOSE_OFFSET_RATIO in config/settings.py."
    )

# --------------------------------------------------------------------------- #
# Suggested settings readout
# --------------------------------------------------------------------------- #
with st.expander("Copy tuned thresholds as environment variables"):
    st.code(
        "\n".join(
            [
                f"export PROCTORING_YOLO_CONFIDENCE={yolo_conf}",
                f"export PROCTORING_POSE_CONFIDENCE={pose_conf}",
                f"export PROCTORING_YOLO_IMG_SIZE={int(imgsz)}",
                f"export PROCTORING_ABSENT_FRAMES={int(absent_frames)}",
                f"export PROCTORING_HEAD_TURN_RATIO={head_ratio}",
            ]
        ),
        language="bash",
    )
    st.caption(
        "Set these before starting the Celery worker / server to apply your tuned "
        f"thresholds. Multiple-person minimum (currently {int(multi_min)}) is set in "
        "config/settings.py."
    )
