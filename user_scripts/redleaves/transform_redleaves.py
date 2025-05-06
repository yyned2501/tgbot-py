from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from filters import custom_filters
from libs.transform import transform
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
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"{bonus}"), SITE_NAME, BONUS_NAME, True)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。") 

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
    async with async_session_maker() as session:
        async with session.begin():             
            try:
                await transform(session, transform_message, Decimal(f"-{bonus}"), SITE_NAME, BONUS_NAME, False)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")
             
