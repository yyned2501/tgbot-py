""" Module to automate message deletion. """

import traceback
from app import scheduler
from libs.log import logger
from libs import others
from emoji import emojize
from datetime import datetime, timedelta, timezone
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message




auto_change_name_init = False
dizzy = emojize(":dizzy:", language="alias")
cake = emojize(":cake:", language="alias")
all_time_emoji_name = [
    "clock12",
    "clock1230",
    "clock1",
    "clock130",
    "clock2",
    "clock230",
    "clock3",
    "clock330",
    "clock4",
    "clock430",
    "clock5",
    "clock530",
    "clock6",
    "clock630",
    "clock7",
    "clock730",
    "clock8",
    "clock830",
    "clock9",
    "clock930",
    "clock10",
    "clock1030",
    "clock11",
    "clock1130",
]
time_emoji_symb = [emojize(f":{s}:", language="alias") for s in all_time_emoji_name]

async def change_name_auto(client:Client):
    try:
        time_cur = (
            datetime.now(timezone.utc)  # 使用 now 方法直接获取 UTC 时间
            .astimezone(timezone(timedelta(hours=8)))  # 转换为东八区时间
            .strftime("%H:%M:%S:%p:%a")  # 格式化输出   
        )
        hour, minu, seco, p, abbwn = time_cur.split(":")
        shift = 1 if int(minu) > 30 else 0
        hsym = time_emoji_symb[(int(hour) % 12) * 2 + shift]
        _last_name = f"{hour}:{minu} {p} UTC+8 {hsym}"
        await client.update_profile(last_name=_last_name)
        me = await client.get_me()
        if me.last_name != _last_name:
            raise Exception("修改 last_name 失败")
    except Exception as e:
        trac = "\n".join(traceback.format_exception(e))
        await logger.info(f"更新失败! \n{trac}")



@Client.on_message(                                                                    
        filters.me
        & filters.command("autochangename")
        )

async def auto_changename(client: Client, message: Message):

    if len(message.command) != 2:
        if not message.reply_to_message:
            return await message.edit(f"命令格式不对请按一下格式输入 \n/autochangename on/off")
    if message.command[1].lower() == 'on':
        if not scheduler.get_job("autochangename"):
            scheduler.add_job(change_name_auto,"cron", second=0, id="autochangename")
        await message.edit(f"自动报时昵称已启用")
        await others.delete_message(message,1)
        logger.info(f"自动报时昵称已启用")
    elif message.command[1].lower() == 'off':
        if scheduler.get_job("autochangename"):
            scheduler.remove_job("autochangename")
        await message.edit(f"自动报时昵称已关闭")
        await others.delete_message(message,1)
        logger.info(f"自动报时昵称已关闭")