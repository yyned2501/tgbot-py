from apscheduler.schedulers.asyncio import AsyncIOScheduler
from libs.state import state_manager

scheduler = AsyncIOScheduler()

from .zhuque.fireGenshinCharacterMagic import zhuque_autofire_firsttimeget

scheduler_jobs = {"autofire": zhuque_autofire_firsttimeget}


async def start_scheduler():
    for job in (schedulers := state_manager.get_section("scheduler", {})):
        if schedulers[job] == "on" and job in scheduler_jobs.keys():
            await scheduler_jobs[job]()


def get_scheduler():
    return scheduler
