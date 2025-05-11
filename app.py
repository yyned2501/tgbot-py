import os
import sys
import json
import asyncio
import platform
import pyrogram
from libs.log import logger
from pyrogram import Client,idle
from models import create_all,async_engine
from user_scripts.zhuque.fireGenshinCharacterMagic_zhuque import zhuque_autofire_firsttimeget
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.config import API_HASH, API_ID, BOT_TOKEN_TEST, PT_GROUP_ID, proxy_set


#
scheduler = AsyncIOScheduler()


if proxy_set['proxy_enable'] == True:
    proxy = proxy_set['proxy']
else:
    proxy = None

async def start_app():
    db_flag_path = "sessions/dbflag.json"
    db_flag_data = None   

    global user_app,bot_app

    user_app = Client(
        "sessions/user_account",
        api_id=API_ID,
        api_hash=API_HASH,
        proxy=proxy,
        plugins=dict(root="user_scripts"),
        )
    """
    bot_app = Client(
        "sessions/bot_account",
        api_id=API_ID,
        api_hash=API_HASH,
        proxy=proxy_set['proxy'],
        plugins=dict(root="bot_scripts"),
        
    )
    """
    logger.info("启动Mytgbot监听程序")
    await user_app.start()
    #await bot_app.start()
    if os.path.exists(db_flag_path):
        try:
            with open(db_flag_path, "r", encoding="utf-8") as f:
                db_flag_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"读取 dbflag.json 失败，将重新初始化数据库：{e}")


    if not db_flag_data or db_flag_data.get('db_flag') != True:
        logger.info("首次运行，初始化数据库...")
        await create_all()
        with open(db_flag_path, "w", encoding="utf-8") as f:
            json.dump({'db_flag': True}, f, ensure_ascii=False, indent=4)
    else:
        logger.info("数据库已初始化，跳过初始化步骤。")

    scheduler.start()
    await zhuque_autofire_firsttimeget()
    logger.info("Mytgbot监听程序启动成功")
    re_mess1,re_mess2 = await system_version_get()
    await user_app.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'], f"Mytgbot 在 {re_mess1}上登录,\n{re_mess2}")
    await idle()
    await async_engine.dispose()
    await user_app.stop()
    #await bot_app.stop()
    logger.info("关闭Mytgbot监听程序")

   


async def system_version_get():
    sys_info = platform.uname()
    python_info = f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    pyrogram_info = f"脚本依赖: pyrogram: {pyrogram.__version__}"
    re_message1 = f"{sys_info.node} 的 {sys_info.system} 设备"
    re_message2 = f"{python_info} {pyrogram_info}"
    return re_message1,re_message2
