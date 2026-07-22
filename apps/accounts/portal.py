from django.shortcuts import render
from django.utils.cache import patch_vary_headers


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def render_portal(request, partial_template, context=None, *, page_title="Exam Proctor"):
    """Full portal shell on normal requests; main-panel fragment for HTMX tab swaps."""
    context = dict(context or {})
    context.setdefault("portal_page_title", page_title)
    if is_htmx(request):
        response = render(request, partial_template, context)
        response["HX-Title"] = page_title
    else:
        context["portal_partial"] = partial_template
        response = render(request, "layouts/portal.html", context)
    # The same URL serves a full shell (normal navigation) or a bare fragment
    # (HTMX tab swap, HX-Request: true). Without Vary, a browser/proxy cache can
    # serve the cached fragment for a normal navigation such as the back button,
    # rendering it as an unstyled "pure HTML" page. Varying keeps the two cache
    # variants separate.
    patch_vary_headers(response, ("HX-Request",))
    return response
