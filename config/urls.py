from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from apps.accounts.media import serve_media
from apps.proctoring import views as proctoring_views
from config import error_views

urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("admin/", admin.site.urls),
    path("courses/", include("apps.courses.urls")),
    path("exams/", include("apps.exams.urls")),
    path("api/v1/proctoring/", include("apps.proctoring.urls")),
    path("faculty/flagged-sessions/", proctoring_views.flagged_sessions, name="flagged_sessions"),
    # Authenticated media. Replaces the open `static(MEDIA_URL, ...)` mount —
    # see apps/accounts/media.py for per-prefix RBAC.
    re_path(r"^media/(?P<rel_path>.+)$", serve_media, name="serve_media"),
    path("unauthorized/", error_views.unauthorized, name="unauthorized"),
]

if settings.DEBUG:
    # Static assets only — never serve MEDIA_ROOT via Django's open static helper.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Branded error pages (404 / 403 / 500) — white empty-state layout.
handler404 = "config.error_views.page_not_found"
handler403 = "config.error_views.permission_denied"
handler500 = "config.error_views.server_error"
