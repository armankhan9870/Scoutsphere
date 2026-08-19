"""Celery worker and beat application instance for asynchronous task queues."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "scoutsphere_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    beat_schedule={
        "run-discovery-every-6-hours": {
            "task": "tasks.run_discovery_job",
            "schedule": 21600.0,  # 6 hours in seconds
        },
    },
)


@celery_app.task(name="tasks.ping")
def ping_task() -> str:
    """Smoke test ping task for Celery worker verification."""
    return "pong"
