import re
from decimal import Decimal
from datetime import datetime, timedelta
from pyrogram import filters, Client
from pyrogram.types import Message
from libs import others
from libs.log import logger
from filters import custom_filters
from config.reply_message import ZQ_REPLY_MESSAGE
from models.transform_db_modle import User, Raiding
from models import async_session_maker

TARGET = [-1001833464786, -1002262543959, -1002522450068]
SITE_NAME = "zhuque"
BONUS_NAME = "灵石"

def extract_lingshi_amount(text: str, pattern: str) -> Decimal | None:
    match = re.search(pattern, text)
    if match:
        return Decimal(match.group(2))
    return None

@Client.on_message(
    filters.chat(TARGET)
    & filters.regex(r"(获得|亏损|你被反打劫|扣税)\s+([\d.]+)\s+灵石\s*$")
    & (custom_filters.zhuque_bot
       | custom_filters.test)
    & custom_filters.reply_to_me    
)
async def zhuque_dajie_Raiding(client: Client, message: Message):
    raiding_msg = await client.get_messages(message.chat.id, message.reply_to_message.reply_to_message_id)
    raidcount_match = re.search(r"^/dajie[\s\S]*\s(\d+)", raiding_msg.text or "")
    raidcount = int(raidcount_match.group(1)) if raidcount_match else 1
    print(raidcount_match)
    print(raidcount)

    gain = extract_lingshi_amount(message.text, r"(获得) ([\d\.]+) 灵石$")
    loss = extract_lingshi_amount(message.text, r"(亏损|你被反打劫) ([\d\.]+) 灵石$")
    print('gain',gain)
    print ('loss',loss)
    if "扣税" in message.text:
        loss = extract_lingshi_amount(message.text, r"(你被反打劫) ([\d\.]+) 灵石$")
        gain = extract_lingshi_amount(message.text, r"(获得) ([\d\.]+) 灵石$")
    print(raiding_msg)
    if gain or loss:
        async with async_session_maker() as session, session.begin():
            try:
                user = await User.get(session, raiding_msg)
                bonus = gain if gain else -loss
                await user.add_raiding_record(session, SITE_NAME, "raiding", raidcount, bonus)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息, 错误：{e}")

@Client.on_message(
    filters.chat(TARGET)
    & (filters.regex(r"(获得|亏损|你被反打劫|扣税) ([\d\.]+) 灵石$") | filters.regex(r"赢局总计|操作过于频繁|不能打劫|修为等阶"))
    & custom_filters.zhuque_bot
    & custom_filters.command_to_me
)
async def zhuque_dajie_be_raided(client: Client, message: Message):
    raiding_msg = message.reply_to_message
    text = message.text
    if "操作过于频繁" in text:
        reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE["dajieCoolingDown"])
        await others.delete_message(reply, 20)
    elif "赢局总计" in text:
        reply_key = "dajieInfoLose" if "总计赢了" in text else "dajieInfoWin"
        reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE[reply_key])
        await others.delete_message(reply, 20)
    elif "不能打劫" in text:
        if "对方灵石低于" in text:
            reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE["meInsufficient"])
        else:
            tmp = await raiding_msg.reply("+1")
            await others.delete_message(tmp, 5)
            reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE["othersInsufficient"])
        await others.delete_message(reply, 20)
    elif "修为等阶" in text:
        reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE["infoBy"])
        await others.delete_message(reply, 20)
    else:
        raidcount_match = re.search(r"^/dajie[\s\S]*\s(\d+)", raiding_msg.text or "")
        raidcount = int(raidcount_match.group(1)) if raidcount_match else 1
        await zhuque_dajie_fanda(2, raidcount, message)

async def zhuque_dajie_fanda(auto_fanda_switch: int, raidcount: int, message: Message):
    raiding_msg = message.reply_to_message
    win_amt = extract_lingshi_amount(message.text, r"(亏损|你被反打劫) ([\\d\.]+) 灵石$")
    lose_amt = extract_lingshi_amount(message.text, r"(获得) ([\\d\.]+) 灵石$")
    if "扣税" in message.text:
        win_amt = extract_lingshi_amount(message.text, r"(你被反打劫) ([\\d\.]+) 灵石$")
        lose_amt = extract_lingshi_amount(message.text, r"(获得) ([\\d\.]+) 灵石$")

    cd_ready = await dajie_cdtime_Calculate()

    if win_amt and auto_fanda_switch == 1:
        if win_amt >= 3000 and cd_ready:
            await raiding_msg.reply(f"/dajie {raidcount} {ZQ_REPLY_MESSAGE['robbedByWin']}")
        elif not cd_ready:
            await raiding_msg.reply(ZQ_REPLY_MESSAGE["robbedByLoseCD"])
        else:
            await raiding_msg.reply(ZQ_REPLY_MESSAGE["robbedBynosidepot"])
        await record_raiding("beraided", win_amt, raidcount, raiding_msg)

    elif lose_amt and auto_fanda_switch == 2:
        if lose_amt >= 3000 and cd_ready:
            await raiding_msg.reply(f"/dajie {raidcount} {ZQ_REPLY_MESSAGE['robbedByLose']}")
        elif not cd_ready:
            await raiding_msg.reply(ZQ_REPLY_MESSAGE["robbedByLoseCD"])
        else:
            await raiding_msg.reply(ZQ_REPLY_MESSAGE["robbedBynosidepot"])

        if lose_amt >= 20000:
            await raiding_msg.reply_to_message.delete()

        await record_raiding("beraided", -lose_amt, raidcount, raiding_msg)

async def record_raiding(action: str, amount: Decimal, count: int, message: Message):
    async with async_session_maker() as session, session.begin():
        try:
            user = await User.get(session, message)
            await user.add_raiding_record(session, SITE_NAME, action, count, amount)
        except Exception as e:
            logger.exception(f"提交失败: 用户消息, 错误：{e}")

async def dajie_cdtime_Calculate() -> bool:
    now = datetime.now()
    try:
        async with async_session_maker() as session, session.begin():
            last_time, raid_cd = await Raiding.get_latest_raiding_createtime(session, SITE_NAME, "raiding")
            return (now - last_time) >= timedelta(minutes=float(raid_cd))
    except Exception as e:
        logger.exception(f"冷却时间检查失败: {e}")
        return False
