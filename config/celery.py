import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("exam_proctor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

CELERY_TASK_ROUTES = {
    "apps.proctoring.tasks.process_proctor_frame": {"queue": "yolo_inference"},
    "apps.proctoring.tasks.verify_id_card": {"queue": "id_verification"},
}
