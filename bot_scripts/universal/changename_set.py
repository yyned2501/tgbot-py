import re
from libs import others
from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import MY_TGID
from libs.state import state_manager
from schedulers import auto_changename_temp





@Client.on_message(filters.chat(MY_TGID) & filters.command("autochangename"))
async def auto_changename(client: Client, message: Message):

    if len(message.command) < 2:
        await message.reply("❌ 参数不足。\n用法：`/autochangename on | off`")
        return
    action = message.command[1].lower()
    valid_modes = { "on", "off"}
    if action not in valid_modes:
        await message.reply("❌ 参数非法。\n有效选项：`on` `off`")
        return
    state_manager.set_section("SCHEDULER", {"changename": action})

    await auto_changename_temp()
    if action == "on":
        await message.reply(f"✅ 自动报时昵称已启用")        
    else:
        await message.reply("🛑 自动报时昵称已关闭")
