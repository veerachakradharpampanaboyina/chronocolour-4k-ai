"""
ChronoColor 4K AI — Celery Application Configuration

Configures Celery with Redis broker, task routing, and worker settings.
"""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "chronocolor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task behavior
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Result expiry (7 days)
    result_expires=604800,

    # Task routing — GPU-intensive tasks go to GPU queue
    task_routes={
        "app.workers.tasks.orchestrator.*": {"queue": "gpu"},
        "app.workers.tasks.analyze.*": {"queue": "cpu"},
        "app.workers.tasks.restore.*": {"queue": "gpu"},
        "app.workers.tasks.superres.*": {"queue": "gpu"},
        "app.workers.tasks.face_restore.*": {"queue": "gpu"},
        "app.workers.tasks.scene_detect.*": {"queue": "gpu"},
        "app.workers.tasks.object_detect.*": {"queue": "gpu"},
        "app.workers.tasks.object_track.*": {"queue": "gpu"},
        "app.workers.tasks.segment.*": {"queue": "gpu"},
        "app.workers.tasks.colorize.*": {"queue": "gpu"},
        "app.workers.tasks.temporal_memory.*": {"queue": "cpu"},
        "app.workers.tasks.optical_flow.*": {"queue": "gpu"},
        "app.workers.tasks.flicker_correct.*": {"queue": "cpu"},
        "app.workers.tasks.hdr_enhance.*": {"queue": "cpu"},
        "app.workers.tasks.reconstruct.*": {"queue": "cpu"},
        "app.workers.tasks.audio_sync.*": {"queue": "cpu"},
    },

    # Default queue
    task_default_queue="default",

    # Task time limits
    task_soft_time_limit=21600,  # 6 hours soft limit
    task_time_limit=28800,       # 8 hours hard limit

    # Worker settings
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (prevent memory leaks)
    worker_max_memory_per_child=8000000,  # 8GB memory limit per worker

    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,

    # Eager mode for testing
    task_always_eager=settings.celery_task_always_eager,
)

# Auto-discover tasks from the tasks package
celery_app.autodiscover_tasks(["app.workers.tasks"])
