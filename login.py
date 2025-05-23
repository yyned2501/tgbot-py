import asyncio
import subprocess
from libs.log import logger
from config.config import PT_GROUP_ID
from pyrogram import Client
from app import system_version_get
from config.config import API_HASH, API_ID,BOT_TOKEN_TEST,proxy_set



if proxy_set['proxy_enable'] == True:
    proxy = proxy_set['proxy']
else:
    proxy = None
async def main():

    user_app = Client(
        "sessions/user_account",
        api_id=API_ID,
        api_hash=API_HASH,
        proxy=proxy
    )


    async with user_app:
        re_mess = await system_version_get()
        await user_app.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'], f"{re_mess} \n注意本次为首次登录")
        logger.info("Mytgbot首次登录成功，登录信息创建成功")
        command = ["supervisorctl", "start", "main"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("启动main成功")
        else:
            print(result.stdout)
            print(result.stderr)


if __name__ == "__main__":
    asyncio.run(main())
