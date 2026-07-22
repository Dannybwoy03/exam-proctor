(function () {
    "use strict";

    const examApp = document.getElementById("exam-app");
    if (!examApp) return;

    const region = document.getElementById("strike-alert-region");
    const template = document.getElementById("strike-alert-template");
    if (!region || !template) return;

    const ACK_URL = examApp.dataset.acknowledgeUrl || "/api/v1/proctoring/violation/acknowledge/";
    const DISPUTE_URL = examApp.dataset.disputeUrl || "/api/v1/proctoring/violation/dispute/";
    const DEFAULT_MAX = parseInt(examApp.dataset.maxStrikes || "5", 10);

    const shown = new Set();
    // Full-screen overlay shows one card at a time; later strikes wait here.
    const queue = [];
    let activeCard = null;

    function csrf() {
        return (typeof CSRF_TOKEN !== "undefined") ? CSRF_TOKEN : "";
    }

    function attemptId() {
        return (typeof ATTEMPT_ID !== "undefined") ? ATTEMPT_ID : examApp.dataset.attemptId;
    }

    function postJson(url, body) {
        return fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf(),
            },
            body: JSON.stringify(body),
        }).then((r) => r.json().catch(() => null)).catch(() => null);
    }

    function syncStrikeCounter(strike, maxStrikes) {
        if (window.proctor && typeof window.proctor.updateStrikes === "function") {
            window.proctor.updateStrikes(strike, maxStrikes);
        }
    }

    function syncBackdrop() {
        region.classList.toggle(
            "strike-alert-region--active",
            region.querySelector(".strike-alert") !== null
        );
    }

    function dismiss(card) {
        card.classList.remove("strike-alert--visible");
        setTimeout(() => {
            card.remove();
            if (activeCard === card) activeCard = null;
            if (queue.length > 0) {
                mount(queue.shift());
            }
            syncBackdrop();
        }, 280);
    }

    function dedupeKey(violationId, strike, message) {
        if (violationId != null && violationId !== "") {
            return "v:" + String(violationId);
        }
        return "m:" + String(strike || 0) + ":" + (message || "");
    }

    function show({ violationId, message, strike, maxStrikes, violationType, info }) {
        const max = parseInt(maxStrikes, 10) || DEFAULT_MAX;
        const strikeNum = parseInt(strike, 10) || 0;
        const key = dedupeKey(violationId, strikeNum, message);
        if (shown.has(key)) return;
        shown.add(key);

        // Informational alerts (e.g. camera lost) carry no strike data; syncing
        // would wrongly reset the "violations remaining" counter to full.
        if (!info) syncStrikeCounter(strikeNum, max);

        const entry = { violationId, message, strikeNum, max, info };
        if (activeCard) {
            queue.push(entry);
        } else {
            mount(entry);
        }
    }

    function mount({ violationId, message, strikeNum, max, info }) {
        const frag = template.content.cloneNode(true);
        const card = frag.querySelector(".strike-alert");
        const titleEl = card.querySelector(".strike-alert-title");
        const msgEl = card.querySelector(".strike-alert-message");
        const subEl = card.querySelector(".strike-alert-sub");
        const ackBtn = card.querySelector(".strike-alert-ack");
        const disputeBtn = card.querySelector(".strike-alert-dispute");

        card.dataset.violationId = violationId == null ? "" : String(violationId);
        msgEl.textContent = message || "Integrity violation detected.";

        const remaining = Math.max(0, max - strikeNum);
        if (info) {
            subEl.textContent = "Acknowledge to dismiss.";
            if (disputeBtn) disputeBtn.hidden = true;
        } else if (remaining === 1) {
            // Penultimate strike: escalate to an unmissable final warning.
            card.classList.add("strike-alert--final");
            if (titleEl) titleEl.hidden = false;
            subEl.textContent =
                "This is your final warning. One more violation will close the exam immediately.";
        } else {
            subEl.textContent =
                remaining > 0
                    ? `${remaining} violation${remaining === 1 ? "" : "s"} remaining before the exam ends. Acknowledge to dismiss.`
                    : "This was your final violation. The exam will end shortly.";
        }

        ackBtn.addEventListener("click", () => {
            ackBtn.disabled = true;
            if (violationId != null && violationId !== "") {
                postJson(ACK_URL, { attempt_id: attemptId(), violation_id: violationId });
            }
            dismiss(card);
        });

        disputeBtn.addEventListener("click", async () => {
            disputeBtn.disabled = true;
            disputeBtn.textContent = "Filing…";
            const result = await postJson(DISPUTE_URL, { attempt_id: attemptId() });
            if (result && result.disputed) {
                subEl.textContent = "Dispute filed — your instructor will review this. Acknowledge to dismiss.";
                disputeBtn.hidden = true;
            } else {
                // Don't tell the student it worked when it didn't.
                subEl.textContent = "Could not file the dispute — check your connection and try again.";
                disputeBtn.disabled = false;
                disputeBtn.textContent = "File Dispute";
            }
        });

        region.appendChild(card);
        activeCard = card;
        syncBackdrop();
        requestAnimationFrame(() => card.classList.add("strike-alert--visible"));
        try { ackBtn.focus({ preventScroll: true }); } catch (e) { /* older browsers */ }
    }

    window.strikeAlerts = { show, syncStrikeCounter };
})();
