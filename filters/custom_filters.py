from pyrogram.types.messages_and_media import Message
from pyrogram.filters import create

async def reply_to_me_filter(_, __, m: Message):
    return bool(
        m.reply_to_message
        and m.reply_to_message.from_user
        and m.reply_to_message.from_user.is_self
        )
reply_to_me = create(reply_to_me_filter)


async def command_to_me_filter(_, __, m: Message):
    return bool(
        m.reply_to_message
        and m.reply_to_message.reply_to_message
        and m.reply_to_message.reply_to_message.from_user
        and m.reply_to_message.reply_to_message.from_user.is_self
        )
command_to_me = create(command_to_me_filter)


async def cms_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 6091424371
        )
cms_bot = create(cms_bot_filter)


async def choujiang_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 6461022460
        )
choujiang_bot = create(choujiang_bot_filter)


async def zhuque_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 5697370563
        )
zhuque_bot = create(zhuque_bot_filter)


async def hddobly_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 6474948384
        )
hddobly_bot = create(hddobly_bot_filter)

async def auth_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.id == 5848633300
        )
auth = create(auth_filter)

async def test_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.id == 6138413603
        )
test = create(test_filter)


async def yyz_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 6296776523
        )
yyz_bot = create(yyz_bot_filter)

async def audiences_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 2053736484
        )
audiences_bot = create(audiences_bot_filter)


async def cmct_bot_filter(_, __, m: Message):
    return bool(
        m.from_user
        and m.from_user.is_bot
        and m.from_user.id == 752250569
        )
cmct_bot = create(cmct_bot_filter)

async def cmct_pay_keyword_filter(_, __, m: Message):
    exclude_keywords = ["转账金额过大", "余额不足", "转账失败"]
    if (m.reply_to_message
        and "+" in m.reply_to_message.text):        
        for keyword in exclude_keywords:
            if keyword in m.text:
                return False
        return True
    return False
cmct_pay_keyword = create(cmct_pay_keyword_filter)
    
        
        




       
