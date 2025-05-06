
from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from filters import custom_filters
from libs.transform import transform
from models import async_session_maker

TARGET = [-1002372175195]
SITE_NAME = "audiences"
BONUS_NAME = "爆米花"


###################收到他人的爆米花转入##################################
@Client.on_message(                                                                    
        filters.chat(TARGET)
        & custom_filters.command_to_me
        & filters.regex(r"送给.*?(\d+).*?手续费")
        & custom_filters.audiences_bot 
    )

async def audiences_transform_get(client:Client, message:Message):
    bonus = message.matches[0].group(1)    
    transform_message = message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"{bonus}"), SITE_NAME, BONUS_NAME,True)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")

###################转出爆米花给他人##################################
@Client.on_message(
        filters.chat(TARGET)
        & custom_filters.reply_to_me 
        & filters.regex(r"送给.*?(\d+).*?手续费")
        & custom_filters.audiences_bot              
        )
async def audiences_transform_pay(client:Client, message:Message):
    bonus = message.matches[0].group(1)    
    transform_message = message.reply_to_message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"-{bonus}"), SITE_NAME, BONUS_NAME,False)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")