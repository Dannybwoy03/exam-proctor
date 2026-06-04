(function () {
    "use strict";

    const FRAME_INTERVAL = 3500;
    const HEARTBEAT_INTERVAL = 10000;
    const STATUS_POLL_INTERVAL = 5000;
    const AUTOSAVE_INTERVAL = 12000;

    const examApp = document.getElementById("exam-app");
    if (!examApp) return;
    const STATUS_URL = examApp.dataset.statusUrl || null;
    const AUTOSAVE_URL = examApp.dataset.autosaveUrl || null;
    const RESUME_URL = examApp.dataset.resumeUrl || null;
    const ATTEMPT_ID_VALUE = examApp.dataset.attemptId;
    const STRICTNESS = (examApp.dataset.strictnessLevel || "level_1").toLowerCase();
    const STRICT_NONE = STRICTNESS === "none";
    const STRICT_LEVEL1 = STRICTNESS === "level_1";
    // Lockdown event types are reported by lockdown.js itself and already
    // surface a strike dialog from its JSON response. Server WS warnings for
    // these types would just duplicate the UI, so we ignore them here.
    const LOCKDOWN_WS_TYPES = new Set([
        "tab_switch",
        "visibility_hidden",
        "focus_lost",
        "exit_fullscreen",
    ]);

    let stream = null;
    let ws = null;
    let serverRemaining = parseInt(examApp.dataset.duration || "0", 10) || 0;
    let lastServerSync = Date.now();
    let pendingAutosave = false;

    async function initWebcam() {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        ["webcam-exam", "dashboard-webcam"].forEach((id) => {
            const video = document.getElementById(id);
            if (video) video.srcObject = stream;
        });
    }

    function captureFrame() {
        const video = document.getElementById("webcam-exam");
        if (!video || !video.videoWidth) return null;
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth || 320;
        canvas.height = video.videoHeight || 240;
        canvas.getContext("2d").drawImage(video, 0, 0);
        return canvas.toDataURL("image/jpeg", 0.7);
    }

    function connectWebSocket() {
        if (!ATTEMPT_ID_VALUE) return;
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        ws = new WebSocket(`${protocol}://${window.location.host}/ws/proctoring/${ATTEMPT_ID_VALUE}/`);
        ws.onmessage = (event) => {
            handleWsEvent(JSON.parse(event.data));
        };
        ws.onclose = () => {
            // Reconnect quickly so the server can resume the disconnect-paused attempt.
            setTimeout(connectWebSocket, 2500);
        };
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "heartbeat" }));
            }
        }, HEARTBEAT_INTERVAL);
    }

    function updateStrikes(strike, max) {
        const el = document.getElementById("strikes");
        if (!el) return;
        const remaining = Math.max(0, max - strike);
        el.textContent = `Violations Remaining: ${remaining}/${max}`;
        el.dataset.currentStrikes = strike;
    }

    function setFaceStatus(status) {
        const tag = document.getElementById("face-status-tag");
        if (!tag) return;
        if (tag.dataset.status === status) return;
        tag.dataset.status = status;
        tag.className = `face-verified-tag face-status-tag--${status}`;
        const label = {
            passed: "FACE VERIFIED",
            failed: "VERIFICATION FAILED",
            pending: "VERIFYING…",
        }[status] || "VERIFYING…";
        tag.textContent = label;
    }

    function handleWsEvent(data) {
        if (data.type === "warning") {
            updateStrikes(data.strike, data.max_strikes);
            // At LEVEL_1, surface the warning dialog for ML-detected violations
            // pushed from the server (lockdown events are already dialog'd by
            // lockdown.js when its own POST returns).
            if (
                STRICT_LEVEL1 &&
                window.lockdown &&
                typeof window.lockdown.showStrikeWarning === "function" &&
                !LOCKDOWN_WS_TYPES.has(data.violation_type)
            ) {
                window.lockdown.showStrikeWarning({
                    strike: data.strike,
                    maxStrikes: data.max_strikes,
                    violationType: data.violation_type,
                });
            }
        }
        if (data.type === "terminate") {
            // Server is the source of truth. Delegate to lockdown's overlay+
            // redirect path so the user sees a consistent end-state.
            const reason = data.reason || "Exam terminated.";
            if (window.lockdown && typeof window.lockdown.endExam === "function") {
                window.lockdown.endExam("server_terminate", "Exam ended — " + reason);
            } else {
                document.getElementById("exam-form")?.submit();
            }
        }
        if (data.type === "connected" && data.resumed) {
            // Server resumed our paused attempt; nothing to do client-side.
        }
    }

    async function postFrame() {
        const frame = captureFrame();
        if (!frame) return;
        const res = await fetch("/api/v1/proctoring/frame/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN,
            },
            body: JSON.stringify({
                attempt_id: ATTEMPT_ID_VALUE,
                frame_base64: frame,
                timestamp: new Date().toISOString(),
                client_events: [],
            }),
        });
        if (res.ok) {
            const data = await res.json();
            if (data.max_strikes != null) {
                updateStrikes(data.session_strikes || 0, data.max_strikes);
            }
        }
    }

    async function pollStatus() {
        if (!STATUS_URL) return;
        try {
            const res = await fetch(STATUS_URL, { credentials: "same-origin" });
            if (!res.ok) return;
            const data = await res.json();
            if (typeof data.remaining_seconds === "number") {
                serverRemaining = data.remaining_seconds;
                lastServerSync = Date.now();
            }
            if (data.id_verification_status) {
                setFaceStatus(data.id_verification_status);
            }
            if (data.max_strikes != null) {
                updateStrikes(data.strike_count || 0, data.max_strikes);
            }
            if (data.attempt_status === "terminated" || data.attempt_status === "expired") {
                window.location.href = `/exams/attempts/${ATTEMPT_ID_VALUE}/result/`;
            }
        } catch (err) {
            console.warn("Status poll failed:", err);
        }
    }

    function buildAutosaveBody() {
        const form = document.getElementById("exam-form");
        if (!form) return null;
        const formData = new FormData(form);
        // Drop the csrf token from the body; we send it via the header.
        formData.delete("csrfmiddlewaretoken");
        const params = new URLSearchParams();
        for (const [k, v] of formData.entries()) {
            // Skip empty values to keep the payload small.
            if (v === "" || v == null) continue;
            params.append(k, v);
        }
        return params;
    }

    async function autosave() {
        if (!AUTOSAVE_URL || pendingAutosave) return;
        const body = buildAutosaveBody();
        if (!body || [...body.keys()].length === 0) return;
        pendingAutosave = true;
        try {
            await fetch(AUTOSAVE_URL, {
                method: "POST",
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                credentials: "same-origin",
                body: body.toString(),
            });
        } catch (err) {
            // Network blip — next interval will retry.
        } finally {
            pendingAutosave = false;
        }
    }

    function startExamLoop() {
        // The proctor frame loop is only useful when strictness > NONE; at
        // NONE the server ignores frames anyway and we save bandwidth + battery.
        if (!STRICT_NONE) {
            setInterval(() => postFrame(), FRAME_INTERVAL);
        }
        setInterval(() => pollStatus(), STATUS_POLL_INTERVAL);
        setInterval(() => autosave(), AUTOSAVE_INTERVAL);
        // Save once on unload so a final tab close still captures pending work.
        window.addEventListener("beforeunload", () => {
            const body = buildAutosaveBody();
            if (!body || !navigator.sendBeacon || !AUTOSAVE_URL) return;
            navigator.sendBeacon(AUTOSAVE_URL, body);
        });
    }

    function startTimer() {
        const el = document.getElementById("timer");
        function render() {
            // Server is the source of truth; we just smooth between polls.
            const driftSeconds = Math.floor((Date.now() - lastServerSync) / 1000);
            let remaining = Math.max(0, serverRemaining - driftSeconds);
            const h = Math.floor(remaining / 3600);
            const m = Math.floor((remaining % 3600) / 60);
            const s = remaining % 60;
            if (el) {
                el.textContent = h > 0
                    ? `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
                    : `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
            }
            if (remaining === 0) {
                document.getElementById("exam-form")?.submit();
            }
        }
        render();
        setInterval(render, 1000);
    }

    // Start the proctoring/timer loops only AFTER the student has clicked
    // "Begin" on the lockdown overlay. lockdown.js dispatches `exam:ready`
    // once fullscreen is engaged and the zero-tolerance handlers are armed.
    document.addEventListener("exam:ready", async () => {
        if (!ATTEMPT_ID_VALUE) return;
        // Webcam + live proctoring only when the exam actually proctors. At
        // NONE we keep the timer + autosave loops but skip camera capture.
        if (!STRICT_NONE) {
            try {
                await initWebcam();
                connectWebSocket();
            } catch (err) {
                console.warn("Webcam unavailable:", err);
            }
        }
        startExamLoop();
        startTimer();
        pollStatus();
    });
})();
