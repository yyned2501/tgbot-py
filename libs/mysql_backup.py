import os
import subprocess
import gzip
from app import scheduler
from datetime import datetime
from pathlib import Path
from config.config import DB_INFO
from datetime import datetime
from libs.log import logger
# === 配置部分 ===
BACKUP_DIR = Path("db_file/mysqlBackup")
RETENTION_DAYS = 8  # 备份保留天数


@scheduler.scheduled_job("cron", minute='*/5', id="zsss")
async def mysql_backup():
    # === 生成带时间戳的备份文件名 ===
    global BACKUP_DIR
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if os.name == "posix":
        if DB_INFO["dbset"] == "mySQL":
            #backup_filename = f"{DB_INFO['db_name']}_backup_{timestamp}.sql.gz"
            backup_filename = f"{DB_INFO['db_name']}_backup_{timestamp}.sql"
            backup_path = BACKUP_DIR / backup_filename  # 拼接完整备份路径
            # === 确保备份目录存在 ===
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # === 执行 mysqldump 并压缩 ===
            try:
                #with gzip.open(backup_path, "wb") as f_out:
                with open(backup_path, "w", encoding="utf-8") as f_out:
                    subprocess.run(
                        [
                            "mysqldump",
                            "--no-tablespaces",
                            "-h", DB_INFO["address"],
                            "-P", str(DB_INFO["port"]),
                            "-u", DB_INFO["user"],
                            f"-p{DB_INFO['password']}",
                            DB_INFO["db_name"]
                        ],
                        check=True,
                        stdout=f_out,
                        text=True  # 自动处理字符串编码
                    )
                    if result.returncode != 0:
                        logger.error(f"数据库备份失败: {result.stderr}")
                        backup_path.unlink(missing_ok=True)  # 删除损坏文件
                        return
                logger.info(f"✅ 数据库备份成功: {backup_path}")
            except Exception as e:
                logger.error(f"❌ 备份异常: {e}")
                backup_path.unlink(missing_ok=True)

            # === 删除 7 天前的旧备份 ===
            now = datetime.now()
            #for file in BACKUP_DIR.glob("*.sql.gz"):
            for file in BACKUP_DIR.glob("*.sql"):
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if (now - mtime).days > RETENTION_DAYS:
                    logger.info(f"删除过期备份：{file}")
                    file.unlink()
        else:
            logger.info(f"当前选择的数据库不为mySQL,不执行自动mySQL备份")
    else:
        logger.info(f"当前系统不为linux系统暂不执行数据库备份")
        

#scheduler.add_job(mysql_backup, 'date', run_date="2025-05-14 18:29:00", id='fire1', replace_existing=True)