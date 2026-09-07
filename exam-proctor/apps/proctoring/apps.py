from django.apps import AppConfig


class ProctoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.proctoring"
    label = "proctoring"

    def ready(self):
        # Preload YOLO weights when Django boots so eager-mode Celery (dev)
        # and the first exam frame don't pay the cold-start cost or fail silently.
        import logging

        from django.conf import settings

        if settings.PROCTORING.get("USE_MOCK_ML"):
            return
        try:
            from ml.yolo_service.loader import load_models

            load_models()
        except Exception as exc:
            logging.getLogger(__name__).warning(
                "Could not preload proctoring ML models: %s", exc
            )
