(function () {
    function setActiveNav(navKey) {
        if (!navKey) return;
        document.querySelectorAll(".portal-nav-link[data-portal-nav]").forEach((link) => {
            link.classList.toggle("active", link.dataset.portalNav === navKey);
        });
    }

    function syncFromMain() {
        const page = document.querySelector("#portal-main .portal-page");
        if (!page) return;
        setActiveNav(page.dataset.portalNav || "");
        const title = page.dataset.portalTitle;
        if (title) {
            document.title = title + " — Exam Proctor";
        }
    }

    // ── Flagged session card hover (timeline flyout) ───────────────────────
    function initFlaggedSessionCards(root) {
        const scope = root || document;
        scope.querySelectorAll(".flagged-session-card-wrap").forEach((wrap) => {
            if (wrap.dataset.flaggedHoverInit) return;
            wrap.dataset.flaggedHoverInit = "1";

            const open = () => {
                wrap.classList.add("flagged-session-card-wrap--open");
                const flyout = wrap.querySelector(".flagged-session-card__flyout");
                if (flyout) flyout.setAttribute("aria-hidden", "false");
            };
            const close = () => {
                wrap.classList.remove("flagged-session-card-wrap--open");
                const flyout = wrap.querySelector(".flagged-session-card__flyout");
                if (flyout) flyout.setAttribute("aria-hidden", "true");
            };

            wrap.addEventListener("mouseenter", open);
            wrap.addEventListener("mouseleave", close);
            wrap.addEventListener("focusin", open);
            wrap.addEventListener("focusout", (event) => {
                if (!wrap.contains(event.relatedTarget)) close();
            });
        });
    }

    function onPortalMainSwap() {
        syncFromMain();
        initFlaggedSessionCards(document.getElementById("portal-main"));
    }

    document.body.addEventListener("htmx:afterSwap", (event) => {
        if (event.detail.target.id === "portal-main") {
            onPortalMainSwap();
        }
    });

    document.body.addEventListener("htmx:pushedIntoHistory", syncFromMain);

    // ── HTMX failure fallback ───────────────────────────────────────────────
    // Without these, a failed tab-load leaves the previous page in #portal-main
    // with no feedback. Fall back to a full navigation so the browser shows
    // the real error (or recovers via a normal page load).
    function portalNavFallback(event) {
        const path = event.detail && event.detail.pathInfo;
        const url = path && (path.finalRequestPath || path.requestPath);
        if (url) {
            window.location.href = url;
        }
    }
    document.body.addEventListener("htmx:responseError", portalNavFallback);
    document.body.addEventListener("htmx:sendError", portalNavFallback);
    document.body.addEventListener("htmx:swapError", portalNavFallback);

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => initFlaggedSessionCards(document));
    } else {
        initFlaggedSessionCards(document);
    }

    document.body.addEventListener("click", (event) => {
        const tabLink = event.target.closest("a[data-portal-tab]");
        if (!tabLink || event.defaultPrevented) return;
        event.preventDefault();
        if (typeof htmx === "undefined") {
            window.location.href = tabLink.href;
            return;
        }
        htmx.ajax("GET", tabLink.href, {
            target: "#portal-main",
            swap: "innerHTML show:none settle:120ms",
            pushUrl: true,
            indicator: "#portal-loading",
        });
    });

    // ── Audit-list row clicks ────────────────────────────────────────────────
    // Mark the clicked row active immediately so the UI feels instant; HTMX
    // attributes on the link itself swap *only* the detail pane (#audit-detail)
    // so the list never re-renders and we never see a flash.
    document.body.addEventListener("click", (event) => {
        const auditRow = event.target.closest("a[data-audit-row]");
        if (!auditRow) return;
        const list = document.getElementById("audit-list");
        if (!list) return;
        list.querySelectorAll(".flagged-session-card.active, .audit-item.active").forEach((el) => el.classList.remove("active"));
        auditRow.classList.add("active");
    });
})();
