from celery import Celery
from app.config import REDIS_URL


# First arg = name (used internally by Celery)
# broker = where tasks are sent TO (Redis queue)
# backend = where results are stored (also Redis)
celery_app = Celery(
    "pr_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

@celery_app.task
def analyze_pr(pr_number, repo_full_name, head_sha, base_sha, pr_title, pr_url):
    """
    This task runs inside the Celery worker (a separate process from FastAPI).
    FastAPI puts this job in Redis. The worker picks it up and runs this function.
    """
    print(f"[Task received] PR #{pr_number} in {repo_full_name}")
    print(f"  head_sha: {head_sha}")
    print(f"  title: {pr_title}")

    return {"status": "received", "pr_number": pr_number}