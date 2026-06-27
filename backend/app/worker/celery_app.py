import os
from celery import Celery
from backend.app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    settings.PROJECT_NAME,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600  # 10 minutes max execution time per doc
)

# Auto-discover tasks from worker folder
celery_app.autodiscover_tasks(["backend.app.worker"])

def is_redis_available() -> bool:
    """Helper to check if Redis is reachable. Used to decide fallback to FastAPI background tasks."""
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=1)
        r.ping()
        return True
    except Exception:
        return False
