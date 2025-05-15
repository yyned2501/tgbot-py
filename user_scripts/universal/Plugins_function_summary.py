import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from libs import others
from config.config import PT_GROUP_ID
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import Forbidden
from pyrogram.errors import FloodWait


mess_path = Path("tempfile/get_media")
@Client.on_message(filters.me & filters.command("re") )
async def forward_to_group(client: Client, message: Message):
    
    if reply := message.reply_to_message:       
        try:
            # 获取重复次数，默认为1
            re_times = int(message.command[1]) if len(message.command) >= 2 and message.command[1].isdigit() else 1
        except (IndexError, ValueError):
            # 捕获IndexError（当命令参数为空）和ValueError（当参数不是数字）并设置re_times为1
            re_times = 1
            await message.delete()

   
        for _ in range(re_times):
            try:
                # 如果聊天没有保护内容，执行转发
                await asyncio.sleep(0.3)
                if not message.chat.has_protected_content:
                    await reply.forward(
                        reply.chat.id, message_thread_id=reply.message_thread_id
                    )
                else:
                    # 否则执行复制操作
                    await reply.copy(
                        reply.chat.id,
                        message_thread_id=message.message_thread_id,
                    )
            except (Forbidden, FloodWait, Exception):
                return
    else:
        #await rem.edit("没有回复消息")
        await others.delete_message(message,5)
        
        


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
    await client.send_document(PT_GROUP_ID['BOT_MESSAGE_CHAT'],file_path)
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
    await client.send_message(PT_GROUP_ID['BOT_MESSAGE_CHAT'],message.text)
"""

@Client.on_message(filters.me & filters.command("helpme"))
async def help_message(client:Client, message: Message):
    reult_mess = await message.edit(
        f"```"
        f"\n/dme 删除消息 /dme 数量 "
        f"\n/re 转发消息 "
        f"\n/blockyword add xxx  115电影查询增加不检索关键字"
        f"\n/blockyword remove xxx  115电影查询删除不检索关键字"
        f"\n/autochangename 更新时间昵称: \n     /autochangename on 打开 \n     /autochangename off  关闭: "
        f"\n/zpr 二次元图片 /zpr 0/1 数量 内容 \n举例: /zpr 0 2 亚丝娜 模糊搜索亚丝娜SFW图片2张（0：SFW  1：NSFW"
        f"\n/jupai  回复文字内容 转为jupai"
        f"\n/xjj 小姐姐视频"
        f"\n/backuplist 获取当前已有数据库备份清单"
        f"\n/dbrestore 序号 还原备份(序号根据backuplist获取)"
        f"\n/u2 /u2s 发u2糖 \nu2 username 数量 留言 \nu2s username username username…… 数量 留言"
        f"\n/prizewheel 朱雀大转盘 /prizewheel 次数"
        f"\n/repackcard 回收背包卡片"
        f"\n/packlist 查询背包卡片"
        f"\n/getinfo 查询个人信息"
        f"\n/gamelist 查询当前菠菜对局"
        f"\n/betgame 对局下注 /betgame 场次 下注金额 队伍  场次/gamelist 返回每局信息前的数字 队伍0或1 wbg vs we 0就是下注wbg"
        f"```"
    )


    
    