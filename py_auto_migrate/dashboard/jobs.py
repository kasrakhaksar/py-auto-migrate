"""Background migration jobs for the dashboard."""

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
import hashlib
import json
from threading import Lock
from uuid import uuid4

from py_auto_migrate.core.logging import get_logger
from py_auto_migrate.core.progress import ProgressTracker


logger = get_logger(__name__)
executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="migration")


@dataclass
class MigrationJob:
    job_id: str
    progress: ProgressTracker
    future: Future | None = None
    summary: dict | None = None


_jobs: dict[str, MigrationJob] = {}
_jobs_lock = Lock()
_active_requests: dict[str, str] = {}


def submit_migration(**kwargs) -> str:
    """Start a migration in a worker and return its status identifier."""
    from py_auto_migrate.dashboard.api import execute_migration

    request_key = hashlib.sha256(
        json.dumps(kwargs, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()

    with _jobs_lock:
        active_job_id = _active_requests.get(request_key)
        if active_job_id is not None:
            return active_job_id

        job_id = uuid4().hex
        progress = ProgressTracker()
        job = MigrationJob(job_id=job_id, progress=progress)
        _jobs[job_id] = job
        _active_requests[request_key] = job_id

    def run() -> None:
        try:
            result = execute_migration(
                progress=progress,
                progress_batch_size=None,
                **kwargs,
            )
            job.summary = result.get("summary")
            progress.finish()
        except Exception as exc:
            logger.exception("Migration job %s failed", job_id)
            progress.fail(str(exc))
        finally:
            with _jobs_lock:
                if _active_requests.get(request_key) == job_id:
                    _active_requests.pop(request_key, None)

    job.future = executor.submit(run)
    return job_id


def get_job_status(job_id: str) -> dict | None:
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return None

    result = job.progress.snapshot.to_dict()
    result["job_id"] = job_id
    result["summary"] = job.summary
    return result
