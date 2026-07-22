(function () {
    "use strict";

    const slides = Array.from(document.querySelectorAll(".question-slide"));
    if (!slides.length) return; // not an exam page (or questions withheld pre-ID)
    const progressEl = document.getElementById("q-progress");
    const mapCells = Array.from(document.querySelectorAll(".qmap-cell"));
    const answeredCountEl = document.getElementById("qmap-answered-count");
    let current = 0;

    // ── Slide navigation ────────────────────────────────────────────────────
    function showSlide(index) {
        if (index < 0 || index >= slides.length) return;
        slides[current].style.display = "none";
        current = index;
        slides[current].style.display = "block";
        if (progressEl) {
            progressEl.textContent = `${current + 1} / ${slides.length}`;
        }
        slides.forEach((slide, i) => {
            const prev = slide.querySelector(".q-prev");
            if (prev) prev.disabled = i === 0;
        });
        updateMapCurrent();
    }

    document.querySelectorAll(".q-next").forEach((btn) => {
        btn.addEventListener("click", () => showSlide(current + 1));
    });

    document.querySelectorAll(".q-prev").forEach((btn) => {
        btn.addEventListener("click", () => showSlide(current - 1));
    });

    // ── MCQ option selection (visual) ───────────────────────────────────────
    document.querySelectorAll(".q-option").forEach((opt) => {
        opt.addEventListener("click", () => {
            const radio = opt.querySelector('input[type="radio"]');
            if (!radio) return;
            radio.checked = true;
            const name = radio.name;
            document.querySelectorAll(`input[name="${name}"]`).forEach((r) => {
                r.closest(".q-option")?.classList.remove("selected");
            });
            opt.classList.add("selected");
            // Re-evaluate map state for this question.
            const slide = opt.closest(".question-slide");
            if (slide) refreshAnsweredState(parseInt(slide.dataset.index, 10));
        });
    });

    // ── Question map: state tracking ────────────────────────────────────────

    function isSlideAnswered(slide) {
        if (!slide) return false;
        // Any checked radio under this slide counts as answered.
        if (slide.querySelector('input[type="radio"]:checked')) return true;
        // Or any textarea/text input with non-empty trimmed value.
        const txt = slide.querySelector("textarea, input[type=text]");
        if (txt && txt.value.trim().length > 0) return true;
        return false;
    }

    function updateMapCurrent() {
        mapCells.forEach((cell, i) => {
            cell.classList.toggle("qmap-cell--current", i === current);
            if (i === current) cell.setAttribute("aria-current", "true");
            else cell.removeAttribute("aria-current");
        });
    }

    function refreshAnsweredState(index) {
        if (typeof index !== "number" || isNaN(index)) return;
        const slide = slides[index];
        const cell = mapCells[index];
        if (!slide || !cell) return;
        const answered = isSlideAnswered(slide);
        cell.classList.toggle("qmap-cell--answered", answered);
        recomputeAnsweredCount();
    }

    function recomputeAnsweredCount() {
        if (!answeredCountEl) return;
        const n = mapCells.filter((c) => c.classList.contains("qmap-cell--answered")).length;
        answeredCountEl.textContent = String(n);
    }

    function refreshAllAnswered() {
        slides.forEach((_, i) => {
            const slide = slides[i];
            const cell = mapCells[i];
            if (!slide || !cell) return;
            cell.classList.toggle("qmap-cell--answered", isSlideAnswered(slide));
        });
        recomputeAnsweredCount();
    }

    // Clicks on map cells jump to that question.
    mapCells.forEach((cell) => {
        cell.addEventListener("click", () => {
            const target = parseInt(cell.dataset.target, 10);
            if (!isNaN(target)) showSlide(target);
        });
    });

    // Listen for any user input on the form to re-evaluate the answered state.
    // 'change' covers radios; 'input' covers textarea/text typing.
    const form = document.getElementById("exam-form");
    if (form) {
        form.addEventListener("input", (e) => {
            const slide = e.target.closest(".question-slide");
            if (slide) refreshAnsweredState(parseInt(slide.dataset.index, 10));
        });
        form.addEventListener("change", (e) => {
            const slide = e.target.closest(".question-slide");
            if (slide) refreshAnsweredState(parseInt(slide.dataset.index, 10));
        });
    }

    // ── "Flag for Review" button + map flag indicator ───────────────────────
    // Local-only bookmark so the student can come back to questions they want
    // to revisit. Persisted in sessionStorage keyed by attempt id so it
    // survives accidental refreshes/lockdown re-renders within the same tab.
    const examApp = document.getElementById("exam-app");
    const attemptId = examApp ? examApp.dataset.attemptId : null;
    const flagKey = attemptId ? `examFlags:${attemptId}` : null;
    const FLAG_LABEL = "Flag for Review";
    const UNFLAG_LABEL = "Unflag question";

    function loadFlags() {
        if (!flagKey) return new Set();
        try {
            return new Set(JSON.parse(sessionStorage.getItem(flagKey) || "[]"));
        } catch {
            return new Set();
        }
    }

    function saveFlags(flags) {
        if (!flagKey) return;
        try {
            sessionStorage.setItem(flagKey, JSON.stringify([...flags]));
        } catch {
            /* sessionStorage may be unavailable (private mode); skip. */
        }
    }

    const flagged = loadFlags();

    function applyFlagToMap(index) {
        const cell = mapCells[index];
        if (!cell) return;
        cell.classList.toggle("qmap-cell--flagged", flagged.has(String(index)));
    }

    function renderFlagButton(btn, index) {
        const isFlagged = flagged.has(String(index));
        btn.classList.toggle("btn-flag--active", isFlagged);
        const labelNode = btn.querySelector(".btn-flag-label");
        const text = isFlagged ? UNFLAG_LABEL : FLAG_LABEL;
        if (labelNode) {
            labelNode.textContent = text;
        } else {
            btn.appendChild(Object.assign(document.createElement("span"), {
                className: "btn-flag-label",
                textContent: text,
            }));
        }
    }

    slides.forEach((slide, index) => {
        const btn = slide.querySelector(".btn-flag");
        if (!btn) return;
        renderFlagButton(btn, index);
        applyFlagToMap(index);
        if (flagged.has(String(index))) {
            slide.classList.add("question-slide--flagged");
        }
        btn.addEventListener("click", () => {
            const key = String(index);
            if (flagged.has(key)) flagged.delete(key);
            else flagged.add(key);
            saveFlags(flagged);
            renderFlagButton(btn, index);
            slide.classList.toggle("question-slide--flagged", flagged.has(key));
            applyFlagToMap(index);
        });
    });

    // Initial paint.
    refreshAllAnswered();
    updateMapCurrent();
})();
