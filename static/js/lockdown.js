(function () {
    "use strict";

    const examApp = document.getElementById("exam-app");
    if (!examApp) return;

    const ATTEMPT_ID_VAL = examApp.dataset.attemptId;
    const AUTOSAVE_URL = examApp.dataset.autosaveUrl || null;
    const RESULT_URL = examApp.dataset.resultUrl || null;
    const CLIENT_EVENT_URL = examApp.dataset.clientEventUrl || "/api/v1/proctoring/client-event/";
    const DISPUTE_URL = examApp.dataset.disputeUrl || "/api/v1/proctoring/violation/dispute/";

    // Strictness drives every branch in this module. Defaults to LEVEL_1 so
    // that a missing attribute fails closed (we proctor by default).
    const STRICTNESS = (examApp.dataset.strictnessLevel || "level_1").toLowerCase();
    const STRICT_NONE = STRICTNESS === "none";
    const STRICT_LEVEL1 = STRICTNESS === "level_1";
    const STRICT_LEVEL2 = STRICTNESS === "level_2";
    const MAX_STRIKES = parseInt(examApp.dataset.maxStrikes || "3", 10);

    // Hard-blocked key combos (devtools, new tab/window, copy/paste). Only
    // armed when strictness > NONE; an open-book exam allows everything.
    const BLOCKED_KEYS = [
        { key: "F12" },
        { ctrl: true, key: "t" },
        { ctrl: true, key: "n" },
        { ctrl: true, key: "w" },
        { ctrl: true, shift: true, key: "i" },
        { ctrl: true, key: "c" },
        { ctrl: true, key: "v" },
    ];

    let examStarted = false;
    let ended = false;
    // Suppresses overlapping violation posts while a warning dialog is open
    // or a previous event is still inflight. Keyed by event type so distinct
    // policy breaches (tab vs fullscreen) still go through.
    const inflight = new Set();

    function buildAutosaveBody() {
        const form = document.getElementById("exam-form");
        if (!form) return null;
        const fd = new FormData(form);
        fd.delete("csrfmiddlewaretoken");
        const params = new URLSearchParams();
        for (const [k, v] of fd.entries()) {
            if (v == null || v === "") continue;
            params.append(k, v);
        }
        return [...params.keys()].length > 0 ? params.toString() : null;
    }

    function flushAutosave() {
        if (!AUTOSAVE_URL) return;
        const body = buildAutosaveBody();
        if (!body) return;
        try {
            fetch(AUTOSAVE_URL, {
                method: "POST",
                keepalive: true,
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: body,
            });
        } catch (err) {
            /* best effort */
        }
    }

    function postClientEvent(type, { keepalive = false } = {}) {
        if (typeof ATTEMPT_ID === "undefined") return Promise.resolve(null);
        try {
            return fetch(CLIENT_EVENT_URL, {
                method: "POST",
                keepalive: keepalive,
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": CSRF_TOKEN,
                },
                body: JSON.stringify({ attempt_id: ATTEMPT_ID, type: type }),
            }).then((r) => r.json().catch(() => null));
        } catch (err) {
            return Promise.resolve(null);
        }
    }

    function showEndOverlay(humanReason) {
        const overlay = document.getElementById("exam-end-overlay");
        const reasonEl = document.getElementById("exam-end-reason");
        if (reasonEl && humanReason) reasonEl.textContent = humanReason;
        if (overlay) overlay.hidden = false;
    }

    /**
     * Terminate the attempt and exit to results. Idempotent. Called when:
     *   - LEVEL_2: any lockdown event fires.
     *   - LEVEL_1: the server tells us the 3rd strike has terminated the attempt.
     *   - WebSocket pushes a `terminate` message.
     */
    function endExam(eventType, humanReason) {
        if (ended) return;
        ended = true;
        flushAutosave();
        if (eventType && STRICT_LEVEL2) {
            // LEVEL_2 reports its own event so the server can terminate; at
            // LEVEL_1 the server has already terminated by the time we land here.
            postClientEvent(eventType, { keepalive: true });
        }
        showEndOverlay(humanReason);
        setTimeout(() => {
            if (RESULT_URL) window.location.href = RESULT_URL;
        }, 1800);
    }

    function describeViolation(eventType, fallback) {
        return ({
            tab_switch: "Tab switched during exam",
            visibility_hidden: "Tab switched during exam",
            focus_lost: "Window lost focus during exam",
            exit_fullscreen: "Fullscreen exited during exam",
        })[eventType] || fallback || "Integrity violation";
    }

    function showStrikeWarning({ strike, maxStrikes, violationType, reason }) {
        const dlg = document.getElementById("strike-warning-dialog");
        if (!dlg || typeof dlg.showModal !== "function") return;
        const body = document.getElementById("strike-warning-body");
        const remaining = Math.max(0, (maxStrikes || MAX_STRIKES) - (strike || 0));
        const human = reason || describeViolation(violationType, violationType);
        if (body) {
            body.innerHTML =
                `The proctoring system has detected a potential integrity violation: <strong>${escapeHtml(human)}</strong>. ` +
                `Violations remaining: <strong>${remaining}/${maxStrikes || MAX_STRIKES}</strong>. ` +
                `Continuing with unauthorized behavior will result in immediate test lockout.`;
        }
        if (!dlg.open) dlg.showModal();
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, (c) => (
            { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
        ));
    }

    function wireStrikeDialog() {
        const dlg = document.getElementById("strike-warning-dialog");
        if (!dlg) return;
        const dispute = document.getElementById("strike-warning-dispute");
        const body = document.getElementById("strike-warning-body");
        if (!dispute) return;

        dispute.addEventListener("click", async () => {
            if (typeof ATTEMPT_ID === "undefined") {
                if (dlg.open) dlg.close("dispute");
                return;
            }
            dispute.disabled = true;
            const originalLabel = dispute.textContent;
            dispute.textContent = "Filing…";
            try {
                const res = await fetch(DISPUTE_URL, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": CSRF_TOKEN,
                    },
                    body: JSON.stringify({ attempt_id: ATTEMPT_ID }),
                });
                const data = await res.json().catch(() => null);
                if (data && data.disputed && body) {
                    // Replace the body so the student sees their action was
                    // received (matches the "Continuing without action" cue
                    // in the warning copy).
                    body.innerHTML =
                        "<strong>Dispute filed.</strong> Your instructor will review this " +
                        "violation. The strike still counts toward your tally until the " +
                        "review is complete.";
                }
            } catch (err) {
                /* network blip — student can still continue */
            } finally {
                dispute.disabled = false;
                dispute.textContent = originalLabel;
                // Auto-close after a brief moment so the student sees confirmation.
                setTimeout(() => {
                    if (dlg.open) dlg.close("dispute");
                }, 1400);
            }
        });
    }

    /**
     * Report a violation at LEVEL_1. The server records the strike via the
     * three-strike rule and tells us whether the attempt is terminated.
     */
    async function reportLevel1Violation(eventType, humanReason) {
        if (inflight.has(eventType)) return;
        inflight.add(eventType);
        const data = await postClientEvent(eventType);
        inflight.delete(eventType);
        if (!data) return;
        if (data.terminated) {
            endExam(eventType, humanReason);
            return;
        }
        showStrikeWarning({
            strike: data.strike,
            maxStrikes: data.max_strikes,
            violationType: eventType,
            reason: humanReason,
        });
    }

    function handleLockdownEvent(eventType) {
        if (ended || !examStarted) return;
        const humanReason = describeViolation(eventType);
        if (STRICT_LEVEL2) {
            endExam(eventType, "Exam ended — " + humanReason.toLowerCase() + ".");
            return;
        }
        if (STRICT_LEVEL1) {
            reportLevel1Violation(eventType, humanReason);
        }
    }

    function enterFullscreen() {
        const el = document.documentElement;
        if (el.requestFullscreen) return el.requestFullscreen();
        if (el.webkitRequestFullscreen) return el.webkitRequestFullscreen();
        return Promise.reject(new Error("Fullscreen API not supported."));
    }

    function wireBeginOverlay() {
        const overlay = document.getElementById("exam-begin-overlay");
        const btn = document.getElementById("exam-begin-btn");
        const errEl = document.getElementById("exam-begin-error");
        if (!overlay || !btn) {
            startExam();
            return;
        }
        btn.addEventListener("click", async () => {
            // "Not strict" exams don't need fullscreen — just begin.
            if (!STRICT_NONE) {
                try {
                    await enterFullscreen();
                } catch (err) {
                    if (errEl) {
                        errEl.hidden = false;
                        errEl.textContent = "Fullscreen was blocked. Allow fullscreen and try again.";
                    }
                    return;
                }
            }
            overlay.hidden = true;
            startExam();
        });
    }

    function wireLockdownHandlers() {
        // Visibility / focus / fullscreen are policed identically at LEVEL_1
        // and LEVEL_2; the dispatcher (handleLockdownEvent) chooses warn vs end.
        document.addEventListener("visibilitychange", () => {
            if (document.hidden) handleLockdownEvent("visibility_hidden");
        });

        window.addEventListener("blur", () => {
            if (!document.hasFocus()) handleLockdownEvent("focus_lost");
        });

        document.addEventListener("fullscreenchange", () => {
            if (!document.fullscreenElement) handleLockdownEvent("exit_fullscreen");
        });

        // Soft blockers — don't terminate, just prevent the action.
        document.addEventListener("keydown", (e) => {
            for (const combo of BLOCKED_KEYS) {
                const ctrlMatch = combo.ctrl ? e.ctrlKey || e.metaKey : true;
                const shiftMatch = combo.shift ? e.shiftKey : !combo.shift || !e.shiftKey;
                if (ctrlMatch && shiftMatch && e.key.toLowerCase() === combo.key.toLowerCase()) {
                    e.preventDefault();
                }
            }
        });

        ["copy", "paste", "cut"].forEach((evt) => {
            document.addEventListener(evt, (e) => e.preventDefault());
        });
    }

    function startExam() {
        examStarted = true;
        if (!STRICT_NONE) {
            wireLockdownHandlers();
            wireStrikeDialog();
        }
        document.dispatchEvent(new CustomEvent("exam:ready"));
    }

    wireBeginOverlay();

    // Public hook so proctor.js (or WebSocket terminate handlers) can also end
    // the exam without re-implementing the autosave / overlay / redirect path.
    window.lockdown = {
        endExam,
        enterFullscreen,
        strictness: STRICTNESS,
        showStrikeWarning,
    };
})();
