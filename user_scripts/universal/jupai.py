
import urllib.parse
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message


ju_pai_api = "https://api.txqq.pro/api/zt.php"

"""
文字转为举牌人图片
"""

@Client.on_message(                                                                    
        filters.me
        & filters.command("jupai")
        )
async def ju_pai(client: Client, message: Message):

    code_message = message
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:
        if len(message.command) >= 2:
            text = ','.join(message.command[1:])            
        else:
            text = None 
    print(text)
    if not text:
        return await message.edit("arg_error")
    try:
        image_url = f"{ju_pai_api}?msg={urllib.parse.quote(text)}"
        await message.reply_photo(
            image_url,
            quote=False,
            reply_to_message_id=message.reply_to_message_id,            
        )
        await code_message.delete()
    except Exception as e:
        await message.edit(f"获取失败 ~ {e.__class__.__name__}")