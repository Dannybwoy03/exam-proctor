(function () {
    "use strict";

    const SKELETON_EDGES = [
        [0, 1], [0, 2], [1, 3], [2, 4], [5, 6], [5, 7], [7, 9], [6, 8],
        [8, 10], [5, 11], [6, 12], [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
    ];

    // The dialog lives inside #audit-detail, which HTMX swaps when a session
    // is selected — so elements are re-queried (and per-element listeners
    // re-wired) lazily instead of being captured once at page load.
    let dialog = null;
    let canvas = null;
    let ctx = null;
    let titleEl = null;
    let metaEl = null;
    let showPose = null;
    let showBoxes = null;
    let clipWrap = null;
    let clipStrip = null;
    let clipPlay = null;

    let current = null;
    let img = new Image();
    let clipImg = new Image();
    let clipMode = false;     // when true, the canvas shows a raw clip frame
    let clipTimer = null;
    let clipIndex = 0;

    function grabElements() {
        dialog = document.getElementById("snapshot-inspector-dialog");
        canvas = document.getElementById("snapshot-inspector-canvas");
        if (!dialog || !canvas) return false;
        ctx = canvas.getContext("2d");
        titleEl = document.getElementById("snapshot-inspector-title");
        metaEl = document.getElementById("snapshot-inspector-meta");
        showPose = document.getElementById("snapshot-show-pose");
        showBoxes = document.getElementById("snapshot-show-boxes");
        clipWrap = document.getElementById("snapshot-clip");
        clipStrip = document.getElementById("snapshot-clip-strip");
        clipPlay = document.getElementById("snapshot-clip-play");
        wirePerElementListeners();
        return true;
    }

    function wirePerElementListeners() {
        if (clipPlay && !clipPlay.dataset.snapInit) {
            clipPlay.dataset.snapInit = "1";
            clipPlay.addEventListener("click", () => {
                const frames = (current && current.clipFrames) || [];
                if (!frames.length) return;
                if (clipTimer) {
                    stopClip();
                    return;
                }
                clipPlay.textContent = "Pause";
                showClipFrame(clipMode ? clipIndex + 1 : 0);
                clipTimer = setInterval(() => showClipFrame(clipIndex + 1), 650);
            });
        }
        [showPose, showBoxes].forEach((el) => {
            if (!el || el.dataset.snapInit) return;
            el.dataset.snapInit = "1";
            el.addEventListener("change", () => {
                // Returning to overlays means leaving clip playback.
                stopClip();
                clipMode = false;
                highlightThumb(-1);
                draw();
            });
        });
    }

    function parseJsonAttr(el, name) {
        const raw = el.getAttribute(name);
        if (!raw) return [];
        try {
            return JSON.parse(raw);
        } catch (e) {
            return [];
        }
    }

    function openInspector(el) {
        current = {
            imageUrl: el.getAttribute("data-image-url"),
            violationType: el.getAttribute("data-violation-type") || "Violation",
            confidence: el.getAttribute("data-confidence") || "",
            timestamp: el.getAttribute("data-timestamp") || "",
            bboxes: parseJsonAttr(el, "data-bboxes"),
            pose: parseJsonAttr(el, "data-pose"),
            gaze: parseJsonAttr(el, "data-gaze"),
            frameWidth: parseInt(el.getAttribute("data-frame-width") || "0", 10),
            frameHeight: parseInt(el.getAttribute("data-frame-height") || "0", 10),
            clipFrames: parseJsonAttr(el, "data-clip-frames"),
        };

        if (titleEl) titleEl.textContent = current.violationType;
        if (metaEl) {
            let meta = `${current.timestamp} · confidence ${current.confidence}`;
            const gaze = current.gaze;
            if (gaze && typeof gaze.h_ratio === "number") {
                meta += ` · gaze h ${gaze.h_ratio.toFixed(2)} / v ${gaze.v_ratio.toFixed(2)}`;
                meta += gaze.off_screen ? " (off-screen)" : " (on-screen)";
            }
            metaEl.textContent = meta;
        }

        const row = document.getElementById(`violation-${el.getAttribute("data-violation-id")}`);
        if (row) row.scrollIntoView({ behavior: "smooth", block: "nearest" });

        img = new Image();
        img.onload = () => {
            clipMode = false;
            resizeCanvas();
            draw();
            renderClip();
            dialog.showModal();
        };
        img.onerror = () => {
            // Broken/expired image URL — still open the dialog with a notice
            // instead of doing nothing when the teacher clicks.
            clipMode = false;
            if (metaEl) metaEl.textContent = "Snapshot image could not be loaded.";
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            renderClip();
            dialog.showModal();
        };
        img.src = current.imageUrl;
    }

    function resizeCanvas() {
        if (!img.naturalWidth) return;
        const maxW = Math.min(720, dialog.clientWidth - 48);
        const scale = maxW / img.naturalWidth;
        canvas.width = Math.round(img.naturalWidth * scale);
        canvas.height = Math.round(img.naturalHeight * scale);
    }

    function drawPose(person, w, h) {
        const kpts = person.keypoints || [];
        ctx.strokeStyle = "#0a3d2e";
        ctx.lineWidth = 2;
        SKELETON_EDGES.forEach(([a, b]) => {
            const pa = kpts[a];
            const pb = kpts[b];
            if (!pa || !pb || pa[2] < 0.3 || pb[2] < 0.3) return;
            ctx.beginPath();
            ctx.moveTo(pa[0] * w, pa[1] * h);
            ctx.lineTo(pb[0] * w, pb[1] * h);
            ctx.stroke();
        });
        kpts.forEach((pt) => {
            if (!pt || pt[2] < 0.3) return;
            ctx.fillStyle = "#0a3d2e";
            ctx.beginPath();
            ctx.arc(pt[0] * w, pt[1] * h, 4, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    function drawBoxes(w, h) {
        (current.bboxes || []).forEach((box) => {
            const x = box.x * w;
            const y = box.y * h;
            const bw = box.w * w;
            const bh = box.h * h;
            ctx.strokeStyle = "#111827";
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, bw, bh);
            ctx.font = "12px sans-serif";
            ctx.fillStyle = "#111827";
            const label = `${box.label || "object"} ${Math.round((box.confidence || 0) * 100)}%`;
            ctx.fillText(label, x + 4, y + 14);
        });
    }

    function draw() {
        if (!current || !img.naturalWidth) return;
        // The clip player owns the canvas while active; toggling an overlay
        // checkbox returns to the annotated snapshot.
        if (clipMode) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const w = canvas.width;
        const h = canvas.height;
        if (showBoxes && showBoxes.checked) drawBoxes(w, h);
        if (showPose && showPose.checked) {
            (current.pose || []).forEach((person) => drawPose(person, w, h));
        }
    }

    function stopClip() {
        if (clipTimer) {
            clearInterval(clipTimer);
            clipTimer = null;
        }
        if (clipPlay) clipPlay.textContent = "Play";
    }

    function highlightThumb(index) {
        if (!clipStrip) return;
        Array.from(clipStrip.children).forEach((el, i) => {
            el.classList.toggle("snapshot-clip-thumb--active", i === index);
        });
    }

    function showClipFrame(index) {
        const frames = (current && current.clipFrames) || [];
        if (!frames.length) return;
        clipIndex = (index + frames.length) % frames.length;
        clipMode = true;
        clipImg = new Image();
        clipImg.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(clipImg, 0, 0, canvas.width, canvas.height);
        };
        clipImg.src = frames[clipIndex];
        highlightThumb(clipIndex);
    }

    function renderClip() {
        stopClip();
        const frames = (current && Array.isArray(current.clipFrames)) ? current.clipFrames : [];
        if (!clipWrap || !clipStrip) return;
        if (!frames.length) {
            clipWrap.hidden = true;
            clipStrip.innerHTML = "";
            return;
        }
        clipWrap.hidden = false;
        clipStrip.innerHTML = "";
        frames.forEach((url, i) => {
            const thumb = new Image();
            thumb.src = url;
            thumb.className = "snapshot-clip-thumb";
            thumb.alt = `Frame ${i + 1}`;
            thumb.addEventListener("click", () => {
                stopClip();
                showClipFrame(i);
            });
            clipStrip.appendChild(thumb);
        });
        highlightThumb(-1);
    }

    // Delegated handlers registered exactly once; they re-resolve the dialog
    // on each interaction so HTMX swapping #audit-detail can't strand them.
    document.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-snapshot-open]");
        if (btn) {
            e.preventDefault();
            if (!grabElements()) return;
            openInspector(btn);
        }
        if (e.target.closest("[data-snapshot-close]") && dialog) {
            stopClip();
            dialog.close();
        }
    });

    window.addEventListener("resize", () => {
        if (dialog && dialog.open && current) {
            resizeCanvas();
            draw();
        }
    });

    document.body.addEventListener("htmx:afterSwap", () => {
        // Swapped-in content replaces the dialog nodes; drop stale references.
        stopClip();
        grabElements();
    });
})();
