import os
import subprocess
import gzip
from datetime import datetime
from pathlib import Path

# === 配置部分 ===
BACKUP_DIR = "/data/mysqlBackup"
MYSQL_USER = "root"
MYSQL_PASSWORD = "StrongRootPass123!"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = "3306"
DATABASE_NAME = "dididadadddd"
RETENTION_DAYS = 7

# === 创建备份文件路径 ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = f"{DATABASE_NAME}_backup_{timestamp}.sql.gz"
backup_path = os.path.join(BACKUP_DIR, backup_filename)

# === 确保目录存在 ===
os.makedirs(BACKUP_DIR, exist_ok=True)

# === 执行 mysqldump 并压缩 ===
print(f"📦 备份 `{DATABASE_NAME}` -> {backup_path}")
try:
    # 打开 gzip 文件作为写入目标
    with gzip.open(backup_path, "wb") as f_out:
        proc = subprocess.run(
            [
                "mysqldump",
                "-h", MYSQL_HOST,
                "-P", MYSQL_PORT,
                "-u", MYSQL_USER,
                f"-p{MYSQL_PASSWORD}",
                DATABASE_NAME
            ],
            check=True,
            stdout=f_out  # 输出重定向到 gzip 文件
        )
    print("✅ 备份完成：", backup_path)
except subprocess.CalledProcessError as e:
    print("❌ mysqldump 失败:", e)

# === 删除 7 天前的旧备份 ===
now = datetime.now()
for file in Path(BACKUP_DIR).glob("*.sql.gz"):
    mtime = datetime.fromtimestamp(file.stat().st_mtime)
    if (now - mtime).days > RETENTION_DAYS:
        print(f"🗑 删除过期备份：{file}")
        file.unlink()
