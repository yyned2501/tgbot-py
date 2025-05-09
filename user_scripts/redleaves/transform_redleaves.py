import os
from libs import others
from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from config import config
from pyrogram.types import Message
from filters import custom_filters
from libs.transform_dispatch import transform
from models import async_session_maker
TARGET = [-1001788987573, -1001873711923]
SITE_NAME = "redleaves"
BONUS_NAME = "魔力"

###################收到他人的魔力转入##################################
@Client.on_message(
        filters.chat(TARGET)
        & filters.regex(r"转账成功,已扣除 (\d+)")
        & custom_filters.yyz_bot
        & custom_filters.command_to_me
    )
async def redleaves_transform_get(client:Client, message:Message):    
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message
    await transform(transform_message, Decimal(f"{bonus}"), SITE_NAME, BONUS_NAME, True)

###################转出魔力给他人##################################
@Client.on_message(
        filters.chat(TARGET)
        & filters.regex(r"转账成功,已扣除 (\d+)")
        & custom_filters.yyz_bot
        & custom_filters.reply_to_me
    )
async def redleaves_transform_pay(client:Client, message:Message):
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message.reply_to_message
    await transform(transform_message, Decimal(f"-{bonus}"), SITE_NAME, BONUS_NAME, False)
             
