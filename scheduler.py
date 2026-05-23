from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import DIGEST_INTERVAL_HOURS

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")


def start_scheduler():
    from agents.summariser import run_digest   # imported here to avoid circular
    scheduler.add_job(
        run_digest,
        trigger="interval",
        hours=DIGEST_INTERVAL_HOURS,
        id="kyra_digest",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    print(f"[Kyra] Scheduler started — digest every {DIGEST_INTERVAL_HOURS} hour(s).")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
