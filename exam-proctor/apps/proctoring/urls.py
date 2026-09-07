from django.urls import path

from . import views

app_name = "proctoring"

urlpatterns = [
    path("id-verify/", views.id_verify, name="id_verify"),
    path("frame/", views.process_frame, name="frame"),
    path("client-event/", views.client_event, name="client_event"),
    path("session/<int:attempt_id>/", views.session_status, name="session_status"),
    path("violation/dispute/", views.dispute_latest_violation, name="dispute_violation"),
    path("violation/clip/", views.violation_clip, name="violation_clip"),
    path("violation/acknowledge/", views.acknowledge_violation, name="acknowledge_violation"),
    path("violation/<int:pk>/review/", views.review_violation, name="review_violation"),
    path("attempt/<int:pk>/invalidate/", views.invalidate_exam_attempt, name="invalidate_attempt"),
]
