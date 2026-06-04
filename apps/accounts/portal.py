from django.shortcuts import render


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def render_portal(request, partial_template, context=None, *, page_title="Exam Proctor"):
    """Full portal shell on normal requests; main-panel fragment for HTMX tab swaps."""
    context = dict(context or {})
    context.setdefault("portal_page_title", page_title)
    if is_htmx(request):
        response = render(request, partial_template, context)
        response["HX-Title"] = page_title
        return response
    context["portal_partial"] = partial_template
    return render(request, "layouts/portal.html", context)
