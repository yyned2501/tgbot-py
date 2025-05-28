import re
from decimal import Decimal
from random import random
from datetime import datetime, timedelta
from pyrogram import filters, Client
from pyrogram.types import Message
from libs import others
from libs.log import logger
from filters import custom_filters
from config.reply_message import ZQ_REPLY_MESSAGE
from models.transform_db_modle import User, Raiding

TARGET = [-1001833464786, -1002262543959, -1002522450068]
SITE_NAME = "zhuque"
BONUS_NAME = "灵石"
fanda_switch = 0
fanxian_switch = False


def extract_lingshi_amount(text: str, pattern: str) -> Decimal | None:
    match = re.search(pattern, text)
    if match:
        return Decimal(match.group(2))
    return None


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.reply_to_me
    & filters.regex(r"(获得|亏损|你被反打劫|扣税)\s+([\d.]+)\s+灵石\s*$")
    & (custom_filters.zhuque_bot | custom_filters.test)
)
async def zhuque_dajie_Raiding(client: Client, message: Message):
    raiding_msg = await client.get_messages(
        message.chat.id, message.reply_to_message.reply_to_message_id
    )
    raidcount_match = re.search(r"^/dajie[\s\S]*\s(\d+)", raiding_msg.text or "")
    raidcount = int(raidcount_match.group(1)) if raidcount_match else 1

    gain = extract_lingshi_amount(message.text, r"(获得) ([\d\.]+) 灵石\s*$")
    loss = extract_lingshi_amount(message.text, r"(亏损|你被反打劫) ([\d\.]+) 灵石\s*$")

    if "扣税" in message.text:
        loss = extract_lingshi_amount(message.text, r"(你被反打劫) ([\d\.]+) 灵石\s*$")
        gain = extract_lingshi_amount(message.text, r"(获得) ([\d\.]+) 灵石\s*$")
    if gain or loss:
        bonus = gain if gain else -loss
        await record_raiding("raided", bonus, raidcount, raiding_msg)


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.command_to_me
    & (
        filters.regex(r"(获得|亏损|你被反打劫|扣税)\s+([\d.]+)\s+灵石\s*$")
        | filters.regex(r"(赢局总计|操作过于频繁|不能打劫|修为等阶)")
    )
    & (custom_filters.zhuque_bot | custom_filters.test)
)
async def zhuque_dajie_be_raided(client: Client, message: Message):
    """
    被打劫、被info监听
    """
    global fanda_switch, fanxian_switch
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
        await zhuque_dajie_fanda(fanda_switch, raidcount, message)


async def zhuque_dajie_fanda(auto_fanda_switch: int, raidcount: int, message: Message):
    """
    自动反打程序
    """
    raiding_msg = message.reply_to_message
    win_amt = extract_lingshi_amount(
        message.text, r"(亏损|你被反打劫) ([\d\.]+) 灵石\s*$"
    )
    lose_amt = extract_lingshi_amount(message.text, r"(获得) ([\d\.]+) 灵石\s*$")
    if "扣税" in message.text:
        win_amt = extract_lingshi_amount(
            message.text, r"(你被反打劫) ([\d\.]+) 灵石\s*$"
        )
        lose_amt = extract_lingshi_amount(message.text, r"(获得) ([\d\.]+) 灵石\s*$")

    if win_amt:
        await record_raiding("beraided", win_amt, raidcount, raiding_msg)
    elif lose_amt:
        await record_raiding("beraided", -lose_amt, raidcount, raiding_msg)

    cd_ready = await dajie_cdtime_Calculate()

    if win_amt or lose_amt:
        is_win = bool(win_amt)
        amount = win_amt if is_win else lose_amt
        message_key = "robbedByWin" if is_win else "robbedByLose"
        fanda_off_key = "robbedwinfandaoff" if is_win else "robbedlosfandaoff"
        fanda_switch_valid = (
            (auto_fanda_switch in (1, 3)) if is_win else (auto_fanda_switch in (2, 3))
        )
        if fanda_switch_valid:
            if amount >= 3000 and cd_ready:
                reply = await raiding_msg.reply(
                    f"/dajie {raidcount} {ZQ_REPLY_MESSAGE[message_key]}"
                )
            elif not cd_ready:
                reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE["robbedByLoseCD"])
            else:
                reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE["robbedBynosidepot"])
        else:
            reply = await raiding_msg.reply(ZQ_REPLY_MESSAGE[fanda_off_key])

        if fanxian_switch:
            if is_win:
                if random() < 0.1:
                    Odds = random()
                    await raiding_msg.reply(f"+{int(float(win_amt) * 0.9 * Odds)}")
                    fanxian_reply = await raiding_msg.reply(
                        f"您触发了一次输后返现，表示对您的止损。倍率为{Odds * 100:.2f} %"
                    )
                    await others.delete_message(fanxian_reply, 20)

        await others.delete_message(reply, 20)

        if not is_win:
            if float(lose_amt) >= 20000:
                await raiding_msg.reply_to_message.delete()


async def record_raiding(action: str, amount: Decimal, count: int, message: Message):
    """
    打劫金额写入数据库
    """
    try:
        user = await User.get(message)
        await user.add_raiding_record(SITE_NAME, action, count, amount)
    except Exception as e:
        logger.exception(f"提交失败: 用户消息, 错误：{e}")


async def dajie_cdtime_Calculate() -> bool:
    """
    打劫CD时间计算
    """
    now = datetime.now()
    try:
        last_time, raid_cd = await Raiding.get_latest_raiding_createtime(
            SITE_NAME, "raiding"
        )
        return (now - last_time) >= timedelta(minutes=float(raid_cd))
    except Exception as e:
        logger.exception(f"冷却时间检查失败: {e}")
        return False


@Client.on_message(filters.me & filters.command("fanda"))
async def zhuque_fanda_switch(client: Client, message: Message):
    """
    自动反打开关监听
    """
    global fanda_switch
    if len(message.command) < 3:
        await message.reply("参数不足。用法：`/fanda lose/win/all on/off`")
        return
    cmd_name = message.command[0].lower()
    action = message.command[1].lower()
    args = message.command[2].lower()

    if action in "lose" or "win" or "all":
        if args == "on":
            if action == "win":
                fanda_switch = 1
                reply = await message.edit(f"“赢”自动反打启动")
            elif action == "lose":
                fanda_switch = 2
                reply = await message.edit(f"“输”自动反打启动")
            elif action == "all":
                fanda_switch = 3
                reply = await message.edit(f"“all”自动反打启动")
        else:
            fanda_switch = 0
            reply = await message.edit(f"自动反打关闭")

        await others.delete_message(reply, 20)


@Client.on_message(filters.me & filters.command("fanxian"))
async def zhuque_dajiefanxian_switch(client: Client, message: Message):
    """
    自动反打开关监听
    """
    global fanda_switch
    if len(message.command) < 2:
        await message.reply("参数不足。用法：`/fanxian on/off`")
        return
    cmd_name = message.command[0].lower()
    action = message.command[1].lower()
    if action not in ("on", "off"):
        await message.reply("无效参数。请使用 `on` 或 `off`")
        return
    enable = action == "on"
    status = "启动" if enable else "停止"

    if cmd_name == "fanxian":
        fanxian_switch = enable
        re_mess = await message.edit(f"打劫返现功能已 {status}！")
    else:
        re_mess = await message.edit("无效命令。支持 `/fanxian")
    if re_mess:
        await others.delete_message(re_mess, 8)
