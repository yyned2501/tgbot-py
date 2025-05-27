import subprocess
from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import MY_TGID
from libs.log import logger


@Client.on_message(filters.chat(MY_TGID) & filters.command("update"))
async def restart_tg_bot(client: Client, message: Message):
    reply_message = await message.reply("检测更新中...")
    result = subprocess.run(["bash", "update"], capture_output=True, text=True)
    if result.returncode == 0:
        await reply_message.edit(result.stdout)
        subprocess.run(["supervisorctl", "restart", "main"])
    else:
        await reply_message.edit(result.stdout)
        logger.error(result.stderr)
