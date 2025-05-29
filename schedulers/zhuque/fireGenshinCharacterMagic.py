import aiohttp
import asyncio
from libs.log import logger
from config.config import ZHUQUE_COOKIE, ZHUQUE_X_CSRF
from typing import Optional, Tuple
from datetime import datetime, timedelta, date
from models.redpocket_db_modle import Redpocket
from schedulers import get_scheduler

SITE_NAME = "zhuque"

cookie_headers = {"Cookie": ZHUQUE_COOKIE, "X-Csrf-Token": ZHUQUE_X_CSRF}
url = "https://zhuque.in/api/gaming/fireGenshinCharacterMagic"


async def fireGenshinCharacterMagic() -> Optional[Tuple[str, float]]:
    """
    调用朱雀 API 释放原神角色技能，返回 code 指令和奖励值 bonus。
    """
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("开始自动朱雀释放")
            async with session.post(
                url, headers=cookie_headers, json={"all": 1}
            ) as response:
                json_response = await response.json()
                if response.status == 200 and json_response:
                    code_command = json_response.get("data", {}).get("code", "")
                    bonus = json_response.get("data", {}).get("bonus", 0)
                    logger.info(f"释放成功，指令: {code_command}，奖励: {bonus}")
                    return code_command, bonus
                else:
                    logger.warning(
                        f"释放失败，状态码: {response.status}，返回: {json_response}"
                    )
        except aiohttp.ClientError as e:
            logger.error(f"请求异常: {e}")
        except Exception as e:
            logger.exception(f"未知异常: {e}")
    return None


async def test():
    """
    测试函数，用于验证 API 调用是否正常。
    """
    logger.info("scheduler log")


################朱雀释放##################################
async def zhuque_autofire_firsttimeget():
    try:
        last_time = await Redpocket.get_today_latest_fire_createtime(
            SITE_NAME, "firegenshin"
        )
    except Exception as e:
        logger.exception(f"提交失败: 用户消息, 错误：{e}")
    if last_time:
        if date.today() - last_time.date() > timedelta(days=1):
            next_time = datetime.now() + timedelta(seconds=10)
        else:
            next_time = last_time + timedelta(days=1)
    else:
        next_time = datetime.now() + timedelta(seconds=30)
    scheduler = get_scheduler()
    scheduler.scheduled_job(
        zhuque_autofire,
        "date",
        run_date=next_time,
        id="firegenshin",
        replace_existing=True,
    )
    scheduler.scheduled_job(
        test,
        "interval",
        seconds=10,
        id="firegenshin",
        replace_existing=True,
    )


async def zhuque_autofire():
    try:
        result1 = await fireGenshinCharacterMagic()
        await asyncio.sleep(2)
        result2 = await fireGenshinCharacterMagic()

        code1, bonus1 = result1 if result1 else ("", 0)
        code2, bonus2 = result2 if result2 else ("", 0)
        total_bonus = bonus1 + bonus2

        success = any("SUCCESS" in code for code in (code1, code2))

        if success and total_bonus > 0:
            next_time = datetime.now() + timedelta(days=1)
            logger.info(
                f"释放成功：共得 {total_bonus} 灵石，下次时间：{next_time.isoformat()}"
            )
            await Redpocket.add_redpocket_record(SITE_NAME, "firegenshin", total_bonus)
        else:
            next_time = datetime.now() + timedelta(minutes=15)
            logger.warning(f"释放失败或无奖励，15分钟后重试：{next_time.isoformat()}")
        scheduler = get_scheduler()
        scheduler.add_job(
            zhuque_autofire,
            "date",
            run_date=next_time,
            id="firegenshin",
            replace_existing=True,
        )

    except Exception as e:
        logger.exception(f"朱雀释放任务异常：{e}")
