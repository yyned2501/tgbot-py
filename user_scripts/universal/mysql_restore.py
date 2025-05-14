import os
import subprocess
import gzip
from app import scheduler,user_app
from datetime import datetime
from pathlib import Path
from config.config import DB_INFO
from datetime import datetime
from libs.log import logger
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

# === 配置部分 ===

BACKUP_DIR = Path("db_file/mysqlBackup")
RETENTION_DAYS = 8  # 备份保留天数

@Client.on_message(filters.me & filters.command("backuplist"))
async def mysql_backup_list(client: Client, message: Message):
    global BACKUP_DIR
    # === 获取所有备份文件（按修改时间倒序） ===
    backup_files = sorted(
        BACKUP_DIR.glob("*.sql.gz"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not backup_files:
        re_mess = "❌ 当前没有数据库备份文件"
    else:
        # 生成编号列表
        backup_list = [f"{i}. {file.name}" for i, file in enumerate(backup_files, 1)]
        backup_text = "\n".join(backup_list)
        re_mess = (
            f"📦 当前数据库备份清单如下：\n\n"
            f"{backup_text}\n\n"
            f"请输入 `/dbrestore 序号` 来还原对应备份"
        )
    
    edit_mess = await message.edit(re_mess)
    await others.delete_message(edit_mess, 20)

@Client.on_message(filters.me & filters.command("dbrestore"))
async def mysql_restore_check(client: Client, message: Message):
    global BACKUP_DIR
    if len(message.command) > 1 and message.command[1].isdigit():        
        index = int(message.command[1])
        backup_files = sorted(Path(BACKUP_DIR).glob("*.sql.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
        if 1 <= index <= len(backup_files):
            print("2")
            selected_file = backup_files[index - 1]
            edit_mess = await message.edit(
                f"\n🔄 开始还原：{selected_file.name} -> 数据库 `{DB_INFO['db_name']}`"
            )
            try:
                with gzip.open(selected_file, "rb") as f_in:
                    subprocess.run(
                        [
                            "mysql",
                            "-h", DB_INFO["address"],
                            "-P", str(DB_INFO["port"]),
                            "-u", DB_INFO["user"],
                            f"-p{DB_INFO['password']}",
                            DB_INFO["db_name"]
                        ],
                        stdin=f_in,
                        check=True
                    )
                await edit_mess.edit(f"✅ 数据库{selected_file.name} 还原完成！")
            except subprocess.CalledProcessError as e:
                await edit_mess.edit(f"❌ 还原失败:{selected_file.name}  {e}")
            except Exception as ex:
                await edit_mess.edit(f"❌ 其他错误:{selected_file.name}  {ex}")
        else:
            await message.edit("❌ 输入的编号无效")
    else:
        await message.edit("❌ 格式错误，请使用：`/dbrestore 编号`")
    await others.delete_message(message, 60)