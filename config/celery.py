import os

from celery import Celery
from celery.signals import worker_process_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("exam_proctor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_process_init.connect
def _load_proctoring_models(**kwargs):
    """Preload YOLO weights and the iris gaze model once per worker child."""
    import logging

    try:
        from ml.yolo_service.loader import load_models

        load_models()
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Could not preload proctoring ML models: %s", exc
        )
    try:
        from ml.gaze_service.loader import load_gaze_model

        load_gaze_model()
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Could not preload iris gaze model: %s", exc
        )
