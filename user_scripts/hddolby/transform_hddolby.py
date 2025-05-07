from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from filters import custom_filters
from libs.transform_dispatch import transform
from models import async_session_maker

TARGET = [-1002131053667]
SITE_NAME = "hddolby"
BONUS_NAME = "鲸币"

###################收到他人的鲸币转入##################################
@Client.on_message(
        filters.chat(TARGET)
        & filters.regex(r"成功转账(\d+)")
        & custom_filters.hddobly_bot
        & custom_filters.command_to_me        
    )
async def hddolby_transform_get(client:Client, message:Message):    
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"{bonus}"), SITE_NAME, BONUS_NAME,True)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")



###################转出鲸币给他人##################################
@Client.on_message(
        filters.chat(TARGET)
        & filters.regex(r"成功转账(\d+)")
        & custom_filters.hddobly_bot
        & custom_filters.reply_to_me        
    )
async def hddolby_transform_pay(client:Client, message:Message):
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"-{bonus}"), SITE_NAME, BONUS_NAME, False)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。") 
             
