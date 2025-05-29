import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

from .zhuque.fireGenshinCharacterMagic import zhuque_autofire

scheduler.add_job(
    zhuque_autofire,
    "date",
    run_date=time.time() + 30,
    id="firegenshin",
    replace_existing=True,
)
