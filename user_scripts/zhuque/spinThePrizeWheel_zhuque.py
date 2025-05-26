import aiohttp
import asyncio
import time
from config.config import MY_TGID,PT_GROUP_ID,ZHUQUE_COOKIE, ZHUQUE_X_CSRF
from pyrogram import filters, Client
from pyrogram.types import Message
from libs import others
from libs.log import logger
from user_scripts.zhuque.getInfo_zhuque import getInfo

PRIZES = {
    1: "改名卡", 2: "神佑7天卡", 3: "邀请卡", 4: "自动释放7天卡",
    5: "20G", 6: "10G", 7: "谢谢惠顾"
}
BONUS_VALUES = {1: 300000, 2: 100000, 3: 80000, 4: 30000}
API_URL = "https://zhuque.in/api/gaming/spinThePrizeWheel"
HEADERS = {
    "Cookie": ZHUQUE_COOKIE,
    "X-Csrf-Token": ZHUQUE_X_CSRF,
}

async def spin_wheel(draws: int):
    stats = {
        "cost": 0, "bonus_back": 0, "upload_in_gb": 0,
        "prize_counts": {k: 0 for k in PRIZES}
    }
    lock = asyncio.Lock()

    async with aiohttp.ClientSession() as session:
        chunk = draws // 4
        extra = draws % 4
        tasks = [
            fetch_batch(chunk + (1 if i < extra else 0), session, stats, lock)
            for i in range(4)
        ]
        await asyncio.gather(*tasks)

    return stats


async def fetch_batch(count, session, stats, lock):
    for _ in range(count):
        try:
            async with session.post(API_URL, headers=HEADERS) as resp:
                if resp.status != 200:
                    logger.warning(f"请求失败 status={resp.status}")
                    continue

                result = await resp.json()
                prize = int(result.get("data", {}).get("prize", -1))
                if prize == -1:
                    continue

                async with lock:
                    stats["prize_counts"][prize] += 1
                    stats["cost"] += 1500
                    if prize in BONUS_VALUES:
                        stats["bonus_back"] += BONUS_VALUES[prize] * 0.8
                    elif prize == 5:
                        stats["upload_in_gb"] += 20
                    elif prize == 6:
                        stats["upload_in_gb"] += 10
        except Exception as e:
            logger.exception(f"抽奖异常: {e}")


@Client.on_message(filters.me & filters.command("prizewheel"))
async def zhuque_ThePrizeWheel(client: Client, message: Message):
    try:
        if len(message.command) != 2 or not message.command[1].isdigit():
            return await send_usage_hint(client, message)

        count = int(message.command[1])
        info = await getInfo()
        available = int(info.get("bonus", 0))

        if count * 1500 > available:
            max_draw = available // 1500
            return await message.reply(                
                f"```\n现有灵石不足，最多可抽奖 {max_draw} 次```",
                
            )

        start = time.time()
        waiting = await message.reply("```\n抽奖中……```")

        stats = await spin_wheel(count)
        elapsed = time.time() - start
        cost, bonus_back, gb = stats["cost"], stats["bonus_back"], stats["upload_in_gb"]
        net_loss = (cost - bonus_back) - (gb / 86.9863 * 10000)
        efficiency = gb / max((cost - bonus_back), 1) * 10000

        summary = "\n".join(
            f"{PRIZES.get(k)} : {v}"
            for k, v in stats["prize_counts"].items() if v > 0
        ) or "无"

        await client.edit_message_text(
            message.chat.id, waiting.id,
            (
                f"**抽奖完成：** 耗时：{elapsed:.3f} 秒\n"
                f"**上传灵石比：** {efficiency:.2f} GB/万灵石\n"
                f"按86.98 GB/万灵石计算净亏：{net_loss:.1f}\n\n"
                f"耗费灵石 : **{cost}**\n"
                f"道具回血 : **{int(bonus_back)}**\n"
                f"获得上传 : **{gb} GB**\n\n"
                f"**明细如下：**\n{summary}"
            )
        )

        if message.chat.id not in {MY_TGID, PT_GROUP_ID["BOT_MESSAGE_CHAT"]}:
            await others.delete_message(message, 1)
            
    except Exception as e:
        logger.exception("抽奖命令错误")
        await message.reply(
            f"发生异常: {e}"
        )


async def send_usage_hint(message: Message):
    await message.reply(

        "```\n格式错误，请使用如下格式：\n/prizewheel 抽奖次数\n例如：/prizewheel 10```",
    )
