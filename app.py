import asyncio
from libs.log import logger
from pyrogram import Client,idle
from models import create_all,async_engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.config import API_HASH, API_ID, BOT_TOKEN_TEST, PT_GROUP_ID, proxy_set
#
scheduler = AsyncIOScheduler()

if proxy_set['proxy_enable'] == True:
    proxy = proxy_set['proxy']
else:
    proxy = None

user_app = Client(
    "./sessions/user_account",
    api_id=API_ID,
    api_hash=API_HASH,
    proxy=proxy_set['proxy']
)

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
    await create_all() 
    scheduler.start()
    logger.info("Mytgbot监听程序启动成功")
    async with user_app:
        await user_app.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'], "Mytgbot监听程序启动成功")

    await idle()
    await async_engine.dispose()
    await user_app.stop()
    #await bot_app.stop()
    logger.info("关闭Mytgbot监听程序")


