from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import MY_TGID
import subprocess
from libs.log import logger


@Client.on_message(filters.chat(MY_TGID) & filters.command("restart"))
async def restart_tg_bot(client: Client, message: Message):
    logger.info("Restarting the bot...")
    await message.reply("重启机器人中，请稍候...")
    command = ["docker", "restart", " $(hostname)"]
    subprocess.run(command)
