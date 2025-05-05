""" Module to automate message deletion. """

import traceback
import random
from app import scheduler
from libs.log import logger
from libs import others
from emoji import emojize
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from datetime import datetime, timedelta, timezone


auto_change_name_init = False

emojis = [chr(i) for i in range(0x1F600, 0x1F637 + 1)]  # 56个表情符号
async def change_name_auto(client:Client):
    try:
        time_cur = (
            datetime.now(timezone.utc)  # 使用 now 方法直接获取 UTC 时间
            .astimezone(timezone(timedelta(hours=8)))  # 转换为东八区时间
            .strftime("%H:%M:%S:%p:%a")  # 格式化输出   
        )

        hour, minu, seco, p, abbwn = time_cur.split(":")        
        # 生成动态后缀
        random_emoji = random.choice(emojis)
        _last_name = f"{random_emoji}{hour}:{minu}"
        await client.update_profile(last_name=_last_name)       
        # 验证更新结果
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
