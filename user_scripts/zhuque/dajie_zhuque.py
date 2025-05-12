"""
import asyncio
import re
from random import randint
from pyrogram import filters, Client
from decimal import Decimal
from pyrogram.enums import ParseMode
from pyrogram.types.messages_and_media import Message
from libs import others
from filters import custom_filters
from libs.log import logger
from datetime import datetime, timedelta
from config.reply_message import ZQ_REPLY_MESSAGE
from config.config import PT_GROUP_ID
from models.transform_db_modle import User,Raiding
from models import async_session_maker

TARGET = [-1001833464786, -1002262543959]
SITE_NAME = "zhuque"
BONUS_NAME = "灵石"

@Client.on_message(
    filters.chat(TARGET)
    & (filters.regex(r"(获得|亏损|你被反打劫|扣税) ([\d\.]+) 灵石$"))
    & custom_filters.zhuque_bot
    & custom_filters.reply_to_me
)  
async def zhuque_dajie_Raiding(client: Client, message: Message):

    raiding_message = message.reply_to_message   
    num = re.search(r"^/dajie[\s\S]*\s(\d+)", raiding_message.text)  
    if num:
        counter_count = num.group(1)
    else:
        counter_count = 1
    
    dajie_nowtime = datetime.now()
    lose_code_self = re.search(r"(亏损|你被反打劫) ([\d\.]+) 灵石$", message.text) 
    win_code_self = re.search(r"(获得) ([\d\.]+) 灵石$", message.text)

    if re.search(r"(扣税) ([\d\.]+) 灵石$", message.text):
        lose_code_self = re.search(r"(你被反打劫) ([\d\.]+) 灵石", message.text)
        win_code_self = re.search(r"(获得) ([\d\.]+) 灵石", message.text)
    if win_code_self:#被打劫赢的情况
        async with async_session_maker() as session:
            async with session.begin():
                try:
                    user = await User.get(session, raiding_message)
                    await user.add_raiding_record(session, SITE_NAME, "raiding", counter_count, Decimal(f"{lose_code_self.group(1)}"))                    
                except Exception as e:
                    logger.exception(f"提交失败: 用户消息, 错误：{e}")

    elif lose_code_self: #被打劫输的情况
        async with async_session_maker() as session:
            async with session.begin():
                try:
                    user = await User.get(session, raiding_message)
                    await user.add_raiding_record(session, SITE_NAME, "raiding", counter_count, Decimal(f"-{lose_code_self.group(1)}"))                    
                except Exception as e:
                    logger.exception(f"提交失败: 用户消息, 错误：{e}")

@Client.on_message(
    filters.chat(TARGET)
    & (filters.regex(r"(获得|亏损|你被反打劫|扣税) ([\d\.]+) 灵石$")
       | filters.regex(r"赢局总计|操作过于频繁|不能打劫|修为等阶")
       ) 
    & custom_filters.zhuque_bot
    & custom_filters.command_to_me  
)      
    
async def zhuque_dajie_be_raided(message: Message):

    raiding_message = message.reply_to_message
    if "操作过于频繁" in message.text:
        send_result = await message.reply_to_message.reply(ZQ_REPLY_MESSAGE["dajieCoolingDown"])
        await others.delete_message(send_result,20)
    elif "赢局总计" in message.text:
        if '总计赢了' in message.text:
            send_result = await message.reply_to_message.reply(ZQ_REPLY_MESSAGE["dajieInfoLose"])                         
        else:
            send_result = await message.reply_to_message.reply(ZQ_REPLY_MESSAGE["dajieInfoWin"])
        await others.delete_message(send_result,20)
    elif '不能打劫' in message.text:
        if '对方灵石低于' in message.text:
            send_result = await message.reply_to_message.reply(ZQ_REPLY_MESSAGE["meInsufficient"])
        else:
            send_result0 = await message.reply_to_message.reply("+1")

            send_result = await message.reply_to_message.reply(ZQ_REPLY_MESSAGE["othersInsufficient"])
            await others.delete_message(send_result0,5)
        await others.delete_message(send_result,20)
    elif '修为等阶' in message.text:
        send_result = await message.reply_to_message.reply(ZQ_REPLY_MESSAGE["infoBy"])
        await others.delete_message(send_result,20)

    else:
       
                  
        num = re.search(r"^/dajie[\s\S]*\s(\d+)", raiding_message.text)
        if num:
            await zhuque_dajie_fanda(2, num.group(1), message)
        else:
            await zhuque_dajie_fanda(2, 1, message)


async def zhuque_dajie_fanda(auto_fanda_switch, raidcount, message: Message):

  
    raiding_message = message.reply_to_message
    win_code = re.search(r"(亏损|你被反打劫) ([\d\.]+) 灵石$", message.text)
    lose_code = re.search(r"(获得) ([\d\.]+) 灵石$", message.text)
    if re.search(r"(扣税) ([\d\.]+) 灵石$", message.text):
        win_code = re.search(r"(你被反打劫) ([\d\.]+) 灵石", message.text)
        lose_code = re.search(r"(获得) ([\d\.]+) 灵石", message.text) 
    
    if win_code:#被打劫赢的情况        
        dajiecd = await dajie_cdtime_Calculate()  #打劫CD时间计算
        if auto_fanda_switch == 1:
            if float(win_code.group(2)) >= 3000:
                if dajiecd:
                    send_result = await raiding_message.reply(f"/dajie {str(raidcount)} {ZQ_REPLY_MESSAGE['robbedByWin']}")
                    dajie_nowtime = datetime.now()                    
                else:
                    send_result = await raiding_message.reply(ZQ_REPLY_MESSAGE["robbedByLoseCD"])
            else:
                send_result = await raiding_message.reply(ZQ_REPLY_MESSAGE["robbedBynosidepot"])                            
        else:
            send_result = await raiding_message.reply(ZQ_REPLY_MESSAGE["robbedwinfandaoff"])
        async with async_session_maker() as session:
            async with session.begin():
                try:
                    user = await User.get(session, raiding_message)
                    await user.add_raiding_record(session, SITE_NAME, "beraided", raidcount, Decimal(f"{win_code.group(2)}"))                    
                except Exception as e:
                    logger.exception(f"提交失败: 用户消息, 错误：{e}")

    elif lose_code: #被打劫输的情况
        dajiecd = await dajie_cdtime_Calculate() #打劫CD时间计算        
        if auto_fanda_switch == 2:
            if float(lose_code.group(2)) >= 3000:
                if dajiecd == 1:
                    send_result = await raiding_message.reply(f"/dajie {str(raidcount)} {ZQ_REPLY_MESSAGE['robbedByLose']}")
                    dajie_nowtime = datetime.now()                    
                elif dajiecd == 0:
                    send_result = await raiding_message.reply(ZQ_REPLY_MESSAGE["robbedByLoseCD"])
            else:
                send_result = await raiding_message.reply(ZQ_REPLY_MESSAGE["robbedBynosidepot"]) 
                        
        else:
            send_result = await raiding_message.reply(ZQ_REPLY_MESSAGE["robbedlosfandaoff"])

        if float(lose_code.group(2)) >= 20000:
            await raiding_message.reply_to_message.delete()  
        async with async_session_maker() as session:
            async with session.begin():
                try:
                    user = await User.get(session, raiding_message)
                    await user.add_raiding_record(session, SITE_NAME, "beraided", raidcount, Decimal(f"-{lose_code.group(2)}"))                    
                except Exception as e:
                    logger.exception(f"提交失败: 用户消息, 错误：{e}")   


async def dajie_cdtime_Calculate():
    file_dajietime =""
    dajie_nowtime = datetime.now()
    async with async_session_maker() as session:
        async with session.begin():
            try:
               lasttime,raid_count = await Raiding.get_latest_raiding_createtime(session, SITE_NAME, "raiding")
                        
            except Exception as e:
                logger.exception(f"提交失败: 用户消息, 错误：{e}")
    
    if dajie_nowtime -lasttime >= timedelta(minutes = float(raid_count)):
        return 1
    else:
        return 0
"""