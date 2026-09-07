/*
 * Registration face scan: live webcam capture that writes a JPEG data URL
 * into the hidden face_scan_data input. The server decodes it, computes the
 * ArcFace embedding (ml/face_id), and stores it on the student profile as
 * the reference for pre-exam identity checks.
 */
(function () {
    "use strict";

    var root = document.getElementById("face-scan");
    if (!root) return;

    var hiddenInput = document.getElementById(root.dataset.inputId);
    var video = root.querySelector(".face-scan-video");
    var canvas = root.querySelector(".face-scan-canvas");
    var photo = root.querySelector(".face-scan-photo");
    var startBtn = root.querySelector("[data-action='start']");
    var captureBtn = root.querySelector("[data-action='capture']");
    var retakeBtn = root.querySelector("[data-action='retake']");
    var statusEl = root.querySelector(".face-scan-status");

    var stream = null;

    function setStatus(text) {
        if (statusEl) statusEl.textContent = text || "";
    }

    function show(el, visible) {
        if (el) el.hidden = !visible;
    }

    function stopStream() {
        if (stream) {
            stream.getTracks().forEach(function (track) { track.stop(); });
            stream = null;
        }
        if (video) video.srcObject = null;
    }

    function enterIdle() {
        stopStream();
        show(video, false);
        show(photo, false);
        show(startBtn, true);
        show(captureBtn, false);
        show(retakeBtn, false);
        setStatus("Camera is off. Start the scan when you are ready.");
    }

    function enterLive() {
        show(video, true);
        show(photo, false);
        show(startBtn, false);
        show(captureBtn, true);
        show(retakeBtn, false);
        setStatus("Center your face in the frame, then capture.");
    }

    function enterCaptured() {
        stopStream();
        show(video, false);
        show(photo, true);
        show(startBtn, false);
        show(captureBtn, false);
        show(retakeBtn, true);
        setStatus("Scan captured. Retake if your face is not clearly visible.");
    }

    function startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setStatus("This browser does not support camera access. Use a recent version of Chrome, Edge, or Firefox.");
            return;
        }
        setStatus("Requesting camera access…");
        navigator.mediaDevices
            .getUserMedia({ video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" }, audio: false })
            .then(function (mediaStream) {
                stream = mediaStream;
                video.srcObject = mediaStream;
                return video.play();
            })
            .then(enterLive)
            .catch(function () {
                stopStream();
                setStatus("Camera access was blocked. Allow camera permission for this site and try again.");
            });
    }

    function capture() {
        if (!stream || !video.videoWidth) {
            setStatus("Camera is not ready yet. Wait a moment and try again.");
            return;
        }
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
        var dataUrl = canvas.toDataURL("image/jpeg", 0.9);
        hiddenInput.value = dataUrl;
        photo.src = dataUrl;
        enterCaptured();
    }

    function retake() {
        hiddenInput.value = "";
        photo.removeAttribute("src");
        startCamera();
    }

    startBtn.addEventListener("click", startCamera);
    captureBtn.addEventListener("click", capture);
    retakeBtn.addEventListener("click", retake);

    window.addEventListener("pagehide", stopStream);

    // Restore the captured state after a failed (non-AJAX) submit re-render.
    if (hiddenInput.value) {
        photo.src = hiddenInput.value;
        enterCaptured();
    } else {
        enterIdle();
    }
})();
