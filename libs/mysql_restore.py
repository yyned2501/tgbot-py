import gzip
import subprocess
import os
from pathlib import Path

# === 配置 ===
BACKUP_DIR = "/data/mysqlBackup"
MYSQL_USER = "root"
MYSQL_PASSWORD = "StrongRootPass123!"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = "3306"
DATABASE_NAME = "dididadadddd"

# === 获取所有备份文件 ===
backup_files = sorted(Path(BACKUP_DIR).glob("*.sql.gz"), reverse=True)
if not backup_files:
    print("❌ 没有找到任何 .sql.gz 备份文件")
    exit(1)

# === 显示备份列表 ===
print("\n📂 发现以下备份文件：")
for i, file in enumerate(backup_files, 1):
    print(f"{i}. {file.name}")

# === 用户选择 ===
while True:
    try:
        selection = int(input("\n请输入要还原的备份编号（例如 1）: "))
        if 1 <= selection <= len(backup_files):
            selected_file = backup_files[selection - 1]
            break
        else:
            print("⚠️ 编号超出范围，请重新输入")
    except ValueError:
        print("⚠️ 请输入数字编号")

# === 执行恢复 ===
print(f"\n🔄 开始还原：{selected_file.name} -> 数据库 `{DATABASE_NAME}`")
try:
    with gzip.open(selected_file, "rb") as f_in:
        subprocess.run(
            [
                "mysql",
                "-h", MYSQL_HOST,
                "-P", MYSQL_PORT,
                "-u", MYSQL_USER,
                f"-p{MYSQL_PASSWORD}",
                DATABASE_NAME
            ],
            stdin=f_in,
            check=True
        )
    print("✅ 数据库还原完成！")
except subprocess.CalledProcessError as e:
    print("❌ 还原失败:", e)
except Exception as ex:
    print("❌ 其他错误:", ex)
