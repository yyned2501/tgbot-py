from apscheduler.schedulers.asyncio import AsyncIOScheduler
from libs.state import state_manager
from libs.log import logger

scheduler = AsyncIOScheduler()


from .zhuque.fireGenshinCharacterMagic import zhuque_autofire_firsttimeget

scheduler_jobs = {"autofire": zhuque_autofire_firsttimeget}


async def start_scheduler():
    for job in (schedulers := state_manager.get_section("SCHEDULER", {})):
        logger.info(f"Checking scheduler job: {job}")
        if schedulers[job] == "on" and job in scheduler_jobs.keys():
            logger.info(f"Starting scheduler job: {job}")
            await scheduler_jobs[job]()
