import shutil
from pathlib import Path
from datetime import datetime
from libs import others
from config.config import GROUP_ID
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

mess_path = Path("data/get_message")

@Client.on_message(filters.me & filters.command("re") )
async def forward_to_group(client:Client, message: Message):
    """
    转发消息至当前群
    """
    await message.delete() 
    await message.reply_to_message.forward(message.chat.id)



@Client.on_message(filters.me & filters.command("getmessage"))   

async def getmessage(client:Client, message: Message):
    """
    获取消息信息
    """

    mess_path.mkdir(parents=True, exist_ok=True)    
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    if message.reply_to_message.text:
        file_name = f"{message.reply_to_message.text[:6]}_{current_time}.txt"
    else:
         file_name = f"{current_time}.txt"

    file_path = mess_path/file_name   
    with open(file_path, 'w') as f:
            f.write(f"{message.reply_to_message}")   
    await client.send_document(GROUP_ID['BOT_MESSAGE_CHAT'],file_path)
    shutil.rmtree("data/get_message")
    await message.delete()




@Client.on_message(filters.me & filters.command("id"))
 
async def testmessage(client: Client, message: Message):
    """
    用户ID查询
    """
    re_mess = ""

    msg = message.reply_to_message or message
    chat_id = msg.chat.id    

    if msg.from_user:
        re_mess = f"\nsender_chat id: {chat_id}\nuser id: {msg.from_user.id}\nusername: {msg.from_user.first_name}"
    elif msg.author_signature:
        re_mess = f"\nsender_chat id: {chat_id}\nauthor_signature: {msg.author_signature}"

    if re_mess:
        result = await message.edit(re_mess)
        await others.delete_message(result, 20)
    else:
         await others.delete_message(message, 1)


"""
@Client.on_message(
        filters.private 
        & filters.user(777000)
    )
async def forward_to_group(client:Client, message: Message):
    
    # 监听Telegram(777000)
        
    logger.info(f"Telegram(777000): {message.text}")
    await client.send_message(GROUP_ID['BOT_MESSAGE_CHAT'],message.text)
"""

@Client.on_message(filters.me & filters.command("helpme"))
async def help_message(client:Client, message: Message):
    reult_mess = await message.edit(
        f"```"
        f"/dme 删除消息 /dme 数量 "
        f"/re 转发消息 "
        f"/autochangename 更新时间昵称: \n     /autochangename on 打开 \n     /autochangename off  关闭: "
        f"/zpr 二次元图片 /zpr 0/1 数量 内容 \n举例: /zpr 0 2 亚丝娜 模糊搜索亚丝娜SFW图片2张（0：SFW  1：NSFW"
        f"/jupai  回复文字内容 转为jupai"
        f"/xjj 小姐姐视频"
        f"/u2 /u2s 发u2糖 \nu2 username 数量 留言 \nu2s username username username…… 数量 留言"
        f"/prizewheel 朱雀大转盘 /prizewheel 次数"
        f"/repackcard 回收背包卡片"
        f"/packlist 查询背包卡片"
        f"/getinfo 查询个人信息"
        f"/gamelist 查询当前菠菜对局"
        f"/betgame 对局下注 /betgame 场次 下注金额 队伍  场次/gamelist 返回每局信息前的数字 队伍0或1 wbg vs we 0就是下注wbg"
        f"```"
    )


    
    