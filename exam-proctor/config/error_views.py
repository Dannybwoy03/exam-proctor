"""Custom HTTP error pages — shared empty-state layout (white background)."""

from django.shortcuts import render
from django.urls import reverse


def _home_url(request):
    if getattr(request, "user", None) and request.user.is_authenticated:
        return reverse("accounts:dashboard")
    return reverse("accounts:login")


def _error_nav(request):
    """Role-aware home + secondary action links for error pages."""
    home_url = _home_url(request)
    if getattr(request, "user", None) and request.user.is_authenticated:
        if request.user.is_student_user:
            explore_url = reverse("exams:available")
            explore_label = "Explore"
        else:
            explore_url = reverse("exams:list")
            explore_label = "Explore"
    else:
        explore_url = reverse("accounts:register")
        explore_label = "Create account"
    return home_url, explore_url, explore_label


def unauthorized(request):
    """Explicit 401 page (e.g. linked from middleware or docs)."""
    return render(request, "401.html", {"home_url": _home_url(request)}, status=401)


def page_not_found(request, exception):
    home_url, explore_url, explore_label = _error_nav(request)
    return render(
        request,
        "404.html",
        {
            "home_url": home_url,
            "explore_url": explore_url,
            "explore_label": explore_label,
        },
        status=404,
    )


def permission_denied(request, exception):
    home_url = _home_url(request)
    # Anonymous users get the 401 unauthorized shell; signed-in users get 403.
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return render(request, "401.html", {"home_url": home_url}, status=401)
    return render(request, "403.html", {"home_url": home_url}, status=403)


def server_error(request):
    # Middleware stack may be partial — fall back to login if user isn't loaded.
    try:
        home_url, explore_url, explore_label = _error_nav(request)
    except Exception:
        home_url = reverse("accounts:login")
        explore_url = reverse("accounts:register")
        explore_label = "Create account"
    return render(
        request,
        "500.html",
        {
            "home_url": home_url,
            "explore_url": explore_url,
            "explore_label": explore_label,
        },
        status=500,
    )
