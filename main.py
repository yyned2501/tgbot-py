import asyncio

from app import start_app
from libs.log import logger
from pyrogram import idle
from libs import mysql_backup


if __name__ == "__main__":
    asyncio.run(start_app())
    print('Connected..', flush=True)