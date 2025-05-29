from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

from .zhuque.fireGenshinCharacterMagic import zhuque_autofire

scheduler.add_job(
    zhuque_autofire, "cron", id="firegenshin", replace_existing=True, minute="*"
)
