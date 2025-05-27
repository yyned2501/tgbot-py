import asyncio
from random import randint
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types.messages_and_media import Message
from pyrogram import filters, Client

from app import Client, logger
from filters import custom_filters

TARGET = [-1002022762746]


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.create_bot_filter(7124396542)  # 象岛机器人ID
    & filters.regex(r"象草: (\d+)\n数量: (\d+)\n口令: (.+)\n")
)
async def get_redpocket_message(client: Client, message: Message):
    match = message.matches[0]
    string = match.group(3)
    logger.info(f"象岛：领取红包 {string}")
    await asyncio.sleep(randint(3, 20))
    await client.send_message(message.chat.id, string, ParseMode.DISABLED)
