from pyrogram import filters, Client
from pyrogram.types import Message

from config.config import MY_TGID
from libs import others
from libs.state import state_manager


@Client.on_message(filters.chat(MY_TGID) & filters.command("fanda"))
async def zhuque_fanda_switch(client: Client, message: Message):
    """
    自动反打开关监听
    """
    if len(message.command) < 3:
        await message.reply("参数不足。用法：`/fanda lose/win/all on/off`")
        return
    action = message.command[1].lower()
    args = message.command[2].lower()

    if action in "lose" or "win" or "all":
        if args == "on":
            if action == "win":
                state_manager.set("zhuque_fanda", 1)
                reply = await message.edit(f"“赢”自动反打启动")
            elif action == "lose":
                state_manager.set("zhuque_fanda", 2)
                reply = await message.edit(f"“输”自动反打启动")
            elif action == "all":
                state_manager.set("zhuque_fanda", 3)
                reply = await message.edit(f"“all”自动反打启动")
        else:
            state_manager.set("zhuque_fanda", 0)
            reply = await message.edit(f"自动反打关闭")

        await others.delete_message(reply, 20)


@Client.on_message(filters.chat(MY_TGID) & filters.command("fanxian"))
async def zhuque_dajiefanxian_switch(client: Client, message: Message):
    """
    自动返现开关监听
    """
    if len(message.command) < 2:
        await message.reply("参数不足。用法：`/fanxian on/off`")
        return
    action = message.command[1].lower()
    if action not in ("on", "off"):
        await message.reply("无效参数。请使用 `on` 或 `off`")
        return
    enable = action == "on"
    status = "启动" if enable else "停止"
    state_manager.set("zhuque_fanxian", enable)
    re_mess = await message.edit(f"打劫返现功能已 {status}！")
    if re_mess:
        await others.delete_message(re_mess, 8)
