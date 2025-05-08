import os
import asyncio
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

    global user_app,bot_app

    user_app = Client(
        "sessions/user_account",
        api_id=API_ID,
        api_hash=API_HASH,
        proxy=proxy_set['proxy'],
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
    if not os.path.exists("sessions/dbflag.txt"):
        logger.info(f"文件不存在，首次运行.初始化数据库")
        await create_all() 
        with open("sessions/dbflag.txt", "w", encoding="utf-8") as f:
            f.write("首次运行数据库初始化记录,勿删。")
    scheduler.start()
    await zhuque_autofire_firsttimeget()
    logger.info("Mytgbot监听程序启动成功")
    await user_app.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'], "Mytgbot监听程序启动成功")

    await idle()
    await async_engine.dispose()
    await user_app.stop()
    #await bot_app.stop()
    logger.info("关闭Mytgbot监听程序")


