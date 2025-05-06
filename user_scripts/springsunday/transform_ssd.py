
import os
from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from filters import custom_filters
from libs.transform import transform
from models import async_session_maker

TARGET = [-1002014253433, 1001173590111]
SITE_NAME = "springsunday"
BONUS_NAME = "茉莉"


###################收到他人的茉莉转入##################################
@Client.on_message(                                                                    
        filters.chat(TARGET)
        & custom_filters.cmct_bot
        & custom_filters.command_to_me
        & custom_filters.cmct_pay_keyword
    )
async def ssd_transform_get(client:Client, message:Message):
    bonus = message.reply_to_message.text[1:]
    transform_message = message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"{bonus}"), SITE_NAME, BONUS_NAME,True)                 
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")

@Client.on_edited_message(
        filters.chat(TARGET)
        & custom_filters.cmct_bot
        & custom_filters.command_to_me
        & custom_filters.cmct_pay_keyword
        )
async def ssd_transform_get_edit(client:Client, message:Message):
    bonus = message.reply_to_message.text[1:]
    transform_message = message.reply_to_message
    async with async_session_maker() as session:
        async with  session.begin():
            try:
                await transform(session, transform_message, Decimal(f"{bonus}"), SITE_NAME, BONUS_NAME,True)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")




###################转出茉莉给他人##################################
@Client.on_message(
        filters.chat(TARGET)
        & custom_filters.cmct_bot
        & custom_filters.reply_to_me
        & custom_filters.cmct_pay_keyword
        )
async def ssd_transform_pay(client:Client, message:Message):
    bonus = message.reply_to_message.text[1:]   
    transform_message = message.reply_to_message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():
            try:
                await transform(session, transform_message, Decimal(f"-{bonus}"), SITE_NAME, BONUS_NAME,False)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")

@Client.on_edited_message(
        filters.chat(TARGET)
        & custom_filters.cmct_bot
        & custom_filters.reply_to_me
        & custom_filters.cmct_pay_keyword
        )
async def ssd_transform_pay_edit(client:Client, message:Message):
    bonus = message.reply_to_message.text[1:]   
    transform_message = message.reply_to_message.reply_to_message
    async with async_session_maker() as session:
        async with session.begin():             
            try:
                await transform(session, transform_message, Decimal(f"-{bonus}"), SITE_NAME, BONUS_NAME,False)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")