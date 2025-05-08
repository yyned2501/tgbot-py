import re
from config.config import PT_GROUP_ID
from libs.log import logger
from filters import custom_filters
from models import async_session_maker
from pyrogram import filters, Client
from pyrogram.types import Message
from models.transform_db_modle import User

TARGET = [-1001833464786, -1002262543959]
SITE_NAME = "zhuque"
BONUS_NAME = "灵石"
redpockets = {}


async def in_redpockets_filter(_, __, m: Message):
    return bool(m.text in redpockets)


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"内容: (.*)\n灵石: .*\n剩余: .*\n大善人: (.*)")
)
async def get_redpocket_gen(client: Client, message: Message):    
    callback_data = message.reply_markup.inline_keyboard[0][0].callback_data
    match = message.matches[0]
    from_user = match.group(2)
    retry_times = 0
    while retry_times<1000:
        result_message = await client.request_callback_answer(message.chat.id, message.id,callback_data)      
        match_result_message = re.search(r"已获得 (\d+) 灵石", result_message.message)       
        if match_result_message:
            bonus = match_result_message.group(1)
            await client.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'],f"```\n朱雀红包{match}:\n 抢了{retry_times+1}次 抢到 {bonus} 灵石")
            async with async_session_maker() as session:
                async with session.begin():
                    try:
                        user = await User.get(session, message)              
                        await  user.add_redpocket_record(session, SITE_NAME, "redpocker", bonus)
                    except Exception as e:
                        logger.exception(f"提交失败: 用户消息, 错误：{e}")
                        await message.reply("转换失败，请稍后再试。")
            return
        retry_times += 1



@Client.on_message(
        filters.chat(TARGET)
        & filters.regex(r"天上掉馅饼啦, \+(\d+\.\d+)")
        & custom_filters.zhuque_bot
        & custom_filters.reply_to_me
    )
async def zhuque_pie(client:Client, message:Message):
    bonus = message.matches[0].group(1)
    
    async with async_session_maker() as session:
        async with session.begin():
            try:
                user = await User.get(session, message)
                await  user.add_redpocket_record(session, SITE_NAME, "zhuepie", bonus)
            except Exception as e:
                logger.exception(f"提交失败: 用户消息, 错误：{e}")
                await message.reply("转换失败，请稍后再试。")


