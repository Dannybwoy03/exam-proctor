"""Shared bootstrap: put the project root on sys.path and configure Django so
the lab can import ``ml.yolo_service`` and read ``settings.PROCTORING`` without a
running server or database.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root = two levels up from this file (ml/lab/bootstrap.py -> root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def setup_django() -> None:
    """Idempotently configure Django for standalone (server-less) use."""
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.apps import apps as django_apps

    if django_apps.ready:
        return

    import django

    django.setup()
