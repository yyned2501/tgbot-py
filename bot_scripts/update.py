from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import MY_TGID
import subprocess
from libs.log import logger


@Client.on_message(filters.chat(MY_TGID) & filters.command("update"))
async def restart_tg_bot(client: Client, message: Message):
    reply_message = await message.reply("检测更新中...")
    command = ["bash", "update"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        await reply_message.edit(f"{result.stdout}")
        
    else:
        await reply_message.edit(result.stdout)
        logger.error(result.stderr)


@Client.on_message(filters.chat(MY_TGID) & filters.command("pwd"))
async def pwd_tg_bot(client: Client, message: Message):
    command = ["pwd"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"{result.stdout}")
        await message.reply(f"{result.stdout}")

    else:
        logger.info(result.stdout)
        logger.error(result.stderr)
