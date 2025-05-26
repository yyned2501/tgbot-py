from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import MY_TGID
import subprocess


@Client.on_message(filters.chat(MY_TGID) & filters.command("restart"))
async def restart_tg_bot(client: Client, message: Message):
    command = ["docker", "restart", " $(hostname)"]
    subprocess.run(command)
