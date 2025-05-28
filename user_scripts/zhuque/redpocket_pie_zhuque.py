import re
import asyncio
from decimal import Decimal
from libs.log import logger
from filters import custom_filters
from config.config import PT_GROUP_ID, MY_TGID
from pyrogram import filters, Client
from pyrogram.types import Message
from models.redpocket_db_modle import Redpocket
from app import get_bot_app

TARGET = [-1001833464786, -1002262543959]
SITE_NAME = "zhuque"
BONUS_NAME = "灵石"
redpockets = {}


async def in_redpockets_filter(_, __, m: Message):
    return bool(m.text in redpockets)


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(
        r"内容: ([\s\S]*?)\n灵石: (\d+(?:\.\d+)?)/\d+(?:\.\d+)?\n剩余: .*?\n大善人: (.*)"
    )
)
async def get_redpocket_gen(client: Client, message: Message):
    bot_app = get_bot_app()
    if message.reply_to_message.from_user.id == MY_TGID:
        try:
            await Redpocket.add_redpocket_record(
                SITE_NAME,
                "redpocker",
                Decimal(f"-{message.matches[0].group(2)}"),
            )
        except Exception as e:
            logger.exception(f"提交失败: 用户消息, 错误：{e}")

    callback_data = message.reply_markup.inline_keyboard[0][0].callback_data
    match = message.matches[0]
    redpocket_name = match.group(1)
    red_from_user = match.group(3)
    retry_times = 0
    while retry_times < 500:
        result_message = await client.request_callback_answer(
            message.chat.id, message.id, callback_data
        )
        await asyncio.sleep(0.2)
        match_result_message = re.search(r"已获得 (\d+) 灵石", result_message.message)
        if match_result_message:
            bonus = match_result_message.group(1)
            await bot_app.send_message(
                PT_GROUP_ID["BOT_MESSAGE_CHAT"],
                f"```\n{red_from_user}发的:\n朱雀红包{redpocket_name}:\n 抢了{retry_times+1}次 成功抢到 {bonus} 灵石",
            )
            try:
                await Redpocket.add_redpocket_record(SITE_NAME, "redpocker", bonus)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息, 错误：{e}")
            return
        retry_times += 1


@Client.on_message(
    filters.chat(TARGET)
    & filters.regex(r"天上掉馅饼啦, \+(\d+\.\d+)")
    & custom_filters.zhuque_bot
    & custom_filters.reply_to_me
)
async def zhuque_pie(client: Client, message: Message):
    bonus = message.matches[0].group(1)
    try:
        await Redpocket.add_redpocket_record(SITE_NAME, "zhuepie", bonus)
    except Exception as e:
        logger.exception(f"提交失败: 用户消息, 错误：{e}")
