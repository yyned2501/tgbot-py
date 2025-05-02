import asyncio
from libs.log import logger
from pyrogram import Client,idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.config import API_HASH, API_ID,BOT_TOKEN_TEST,proxy_set
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
    logger.info("启动主程序")
    await user_app.start()
    #await bot_app.start()    
    scheduler.start()
    logger.info("监听主程序")
    await idle()
    await user_app.stop()
    #await bot_app.stop()
    logger.info("关闭主程序")


