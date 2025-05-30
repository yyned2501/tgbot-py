
import os
from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from pyrogram.types import Message
from filters import custom_filters
from libs.transform_dispatch import transform
from libs.state import state_manager

TARGET = [-1002014253433, -1001173590111]
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
    leaderboard = state_manager.get_item(SITE_NAME.upper(),"leaderboard","off")
    notification = state_manager.get_item(SITE_NAME.upper(),"notification","off")
    await transform(
        transform_message,
        Decimal(f"{bonus}"),
        SITE_NAME, BONUS_NAME,
        "get",
        leaderboard,
        "off",
        notification
    )

@Client.on_edited_message(
        filters.chat(TARGET)
        & custom_filters.cmct_bot
        & custom_filters.command_to_me
        & custom_filters.cmct_pay_keyword
        )
async def ssd_transform_get_edit(client:Client, message:Message):
    bonus = message.reply_to_message.text[1:]
    transform_message = message.reply_to_message
    leaderboard = state_manager.get_item(SITE_NAME.upper(),"leaderboard","off")
    notification = state_manager.get_item(SITE_NAME.upper(),"notification","off")
    await transform(
        transform_message,
        Decimal(f"{bonus}"),
        SITE_NAME, BONUS_NAME,
        "get",
        leaderboard,
        "off",
        notification
    )




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
    payleaderboard = state_manager.get_item(SITE_NAME.upper(),"payleaderboard","off")
    notification = state_manager.get_item(SITE_NAME.upper(),"notification","off")
    await transform(
        transform_message,
        Decimal(f"-{bonus}"),
        SITE_NAME, BONUS_NAME,
        "pay",
        "off",
        payleaderboard,
        notification
    )

@Client.on_edited_message(
        filters.chat(TARGET)
        & custom_filters.cmct_bot
        & custom_filters.reply_to_me
        & custom_filters.cmct_pay_keyword
        )
async def ssd_transform_pay_edit(client:Client, message:Message):
    bonus = message.reply_to_message.text[1:]   
    transform_message = message.reply_to_message.reply_to_message
    payleaderboard = state_manager.get_item(SITE_NAME.upper(),"payleaderboard","off")
    notification = state_manager.get_item(SITE_NAME.upper(),"notification","off")
    await transform(
        transform_message,
        Decimal(f"-{bonus}"),
        SITE_NAME, BONUS_NAME,
        "pay",
        "off",
        payleaderboard,
        notification
    )