import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
from app.ingestion.rss_worker import poll_all_feeds

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
_state = {"last_run": None, "articles_processed": 0, "running": False}


def get_scheduler() -> AsyncIOScheduler | None:
    return _scheduler


def get_state() -> dict:
    return {**_state, "scheduler_running": _scheduler is not None and _scheduler.running}


async def _run_ingestion(driver):
    if _state["running"]:
        logger.info("Ingestion already running, skipping")
        return
    _state["running"] = True
    try:
        logger.info("Starting RSS ingestion run...")
        count = await poll_all_feeds(driver)
        _state["articles_processed"] += count
        _state["last_run"] = datetime.utcnow().isoformat()
        logger.info(f"Ingestion complete: {count} articles processed")
    except Exception as e:
        logger.error(f"Ingestion run failed: {e}")
    finally:
        _state["running"] = False


def start_scheduler(driver):
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _run_ingestion,
        "interval",
        hours=settings.ingest_interval_hours,
        args=[driver],
        id="rss_ingestion",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(f"Scheduler started: RSS ingestion every {settings.ingest_interval_hours} hours")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None


async def trigger_ingestion(driver):
    await _run_ingestion(driver)
