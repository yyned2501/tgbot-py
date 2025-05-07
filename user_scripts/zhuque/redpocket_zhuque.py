from libs.log import logger
from decimal import Decimal
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from filters import custom_filters
from libs.transform import transform
from models import async_session_maker



TARGET = -1001833464786

redpockets = {}


async def in_redpockets_filter(_, __, m: Message):
    return bool(m.text in redpockets)


@app.on_message(
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
            await app.send_message("me",f"```\n朱雀红包{match}:\n 抢了{retry_times+1}次 抢到 {bonus} 灵石")
            
            await db_date_write(db_info["db_name"],setdbname,"redpocket","+" + str(bonus)) #写数据库db_date_write  
            return
        retry_times += 1
