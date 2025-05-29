import re
from pyrogram import filters, Client
from pyrogram.types import Message

from config.config import MY_TGID
from libs import others
from libs.state import state_manager

@Client.on_message(filters.chat(MY_TGID) & filters.command(["leaderboard", "payleaderboard","notification"]))
async def scheduler_switch_handler(client: Client, message: Message):
    """
    控制调度任务的开关（如自动释放技能、自动更改昵称）。
    用法: /leaderboard website on|off 或 /payleaderboard website on|off 或 /notification website on|off
    """

    if len(message.command) < 2:
        await message.reply("❌ 参数不足。\n用法：`/autofire website on|off` 或 `/autochangename website on|off`")
        return
    command = message.command[0].lower().lstrip('/')
    website = message.command[1].lower()
    action = message.command[2].lower()
    valid_modes = {"on", "off"}
    websites = {"zhuque","audiences","ptvicomo","hddolby","redleaves","springsunday"}
    if action not in valid_modes:
        await message.reply("❌ 参数非法。\n有效选项：`on` `off`")
        return
    if website not in websites:
        await message.reply(f"❌ 参数非法。\n有效选项：{websites}")
        return
    header = website.upper()
    state_manager.set_section(header, {command: action})
    if action == "off":
        await message.reply(f"🛑 `{website}站点 {command}` 模式已关闭")
    else:
        await message.reply(f"✅ `{website}站点 {command}` 模式已开启")
       