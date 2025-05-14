import subprocess
import gzip
from app import scheduler
from datetime import datetime
from pathlib import Path
from config.config import DB_INFO
from datetime import datetime
# === 配置部分 ===
BACKUP_DIR = Path("db_file/mysqlBackup")
RETENTION_DAYS = 7  # 备份保留天数


def mysql_backup():

    # === 生成带时间戳的备份文件名 ===
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    
    if DB_INFO["dbset"] == "mySQL":
        backup_filename = f"{DB_INFO['db_name']}_backup_{timestamp}.sql.gz"
        backup_path = BACKUP_DIR / backup_filename  # 拼接完整备份路径

        # === 确保备份目录存在 ===
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # === 执行 mysqldump 并压缩 ===
        try:
            with gzip.open(backup_path, "wb") as f_out:
                subprocess.run(
                    [
                        "mysqldump",
                        "-h", DB_INFO["address"],
                        "-P", str(DB_INFO["port"]),
                        "-u", DB_INFO["user"],
                        f"-p{DB_INFO['password']}",
                        DB_INFO["db_name"]
                    ],
                    check=True,
                    stdout=f_out
                )
            print("✅ 备份完成：", backup_path)
        except subprocess.CalledProcessError as e:
            print("❌ mysqldump 失败:", e)

        # === 删除 7 天前的旧备份 ===
        now = datetime.now()
        for file in BACKUP_DIR.glob("*.sql.gz"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if (now - mtime).days > RETENTION_DAYS:
                print(f"🗑 删除过期备份：{file}")
                file.unlink()

scheduler.add_job(mysql_backup, 'date', run_date="2025-05-14 17:58:00", id='fire1', replace_existing=True)