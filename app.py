import os
import json
import asyncio
from pathlib import Path
from libs.log import logger
from pyrogram import Client,idle
from models import create_all,async_engine
from libs.sys_info import system_version_get
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.config import API_HASH, API_ID, PT_GROUP_ID, proxy_set
from user_scripts.zhuque.fireGenshinCharacterMagic_zhuque import zhuque_autofire_firsttimeget
#
scheduler = AsyncIOScheduler()


if proxy_set['proxy_enable'] == True:
    proxy = proxy_set['proxy']
else:
    proxy = None


async def keep_alive_task():
    logger.info("[保活任务] 启动")
    try:
        while True:
            try:
                # 限制 get_me 超时时间
                me = await asyncio.wait_for(user_app.get_me(), timeout=10)
                logger.info("[保活任务] 连接正常：%s", me.username)
            except asyncio.TimeoutError:
                logger.warning("[保活任务] get_me 超时，准备重连")                
            except Exception as e:
                logger.error("[保活任务] 连接异常: %s", e)
                try:
                    await user_app.stop()
                    await asyncio.sleep(3)
                    await user_app.start()
                    logger.info("[保活任务] 已重新连接")
                except Exception as e2:
                    logger.error("[保活任务] 重连失败: %s", e2)
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("[保活任务] 被取消，退出任务")



async def start_app():
    db_flag_path = Path("db_file/dbflag/dbflag.json")
    db_flag_path.parent.mkdir(parents=True, exist_ok=True)    
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
    re_mess = await system_version_get()
    await user_app.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'], re_mess)
    try:
        await asyncio.gather(
            keep_alive_task(),
            idle()
        )
    finally:
        # 程序退出时进行清理
        await async_engine.dispose()
        await user_app.stop()
        logger.info("关闭 Mytgbot 监听程序")
def get_user_bot():
    global user_app 
    return user_app
