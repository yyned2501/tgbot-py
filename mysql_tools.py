# mysql_tools.py

import asyncio
import aiomysql
from decimal import Decimal
from libs.log import logger
from config.config import DB_INFO




# 创建数据库连接池
async def get_pool():
    return await aiomysql.create_pool(
        host=DB_INFO['address'],
        port=DB_INFO['port'],
        user=DB_INFO['user'],
        password=DB_INFO['password'],
        database=DB_INFO['db_name'],       
        autocommit=True
    )

# 执行 SQL（自动连接池和关闭）
async def execute(sql, args=None, fetchone=False, fetchall=False):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, args or ())
            if fetchone:
                result = await cur.fetchone()
            elif fetchall:
                result = await cur.fetchall()
            else:
                result = None
    pool.close()
    await pool.wait_closed()
    return result

# 修改表结构以添加缺失字段
async def add_missing_column(table: str, column: str, column_type: str):
    sql_check = f"SHOW COLUMNS FROM `{table}` LIKE %s"
    result = await execute(sql_check, (column,), fetchone=True)
    if not result:
        sql_add = f"ALTER TABLE `{table}` ADD COLUMN `{column}` {column_type}"
        await execute(sql_add)
        print(f"Added column `{column}` to `{table}`.")

# 写入数据（自动插入或更新）
async def write_data(table: str, data: dict, unique_keys: list):
    columns = ', '.join(f"`{k}`" for k in data)
    values = ', '.join(['%s'] * len(data))
    updates = ', '.join(f"`{k}`=VALUES(`{k}`)" for k in data if k not in unique_keys)

    sql = (
        f"INSERT INTO `{table}` ({columns}) VALUES ({values}) "
        f"ON DUPLICATE KEY UPDATE {updates}"
    )
    await execute(sql, list(data.values()))


# 求和字段（如积分总和）
async def get_sum(table: str, field: str, where: str = "", args: tuple = ()):
    sql = f"SELECT SUM(`{field}`) as total FROM `{table}` {where}"
    result = await execute(sql, args, fetchone=True)
    return result['total'] if result else 0


# 获取计数（比如总人数）
async def get_count(table: str, where: str = "", args: tuple = ()):
    sql = f"SELECT COUNT(*) as count FROM `{table}` {where}"
    result = await execute(sql, args, fetchone=True)
    return result['count'] if result else 0


# 获取排行榜
async def get_top(table: str, field: str, limit=10, where="", args=(), name_field="user_name"):
    sql = (
        f"SELECT `{name_field}`, `{field}` FROM `{table}` "
        f"{where} ORDER BY `{field}` DESC LIMIT {limit}"
    )
    return await execute(sql, args, fetchall=True)


# 格式化排行榜为字符串
def format_top(data, title="排行榜", field_name="积分", name_field="user_name"):
    lines = [f"🏆 {title} 🏆"]
    medals = ["🥇", "🥈", "🥉"]
    for i, row in enumerate(data):
        name = row.get(name_field, "未知")
        value = row.get(field_name, 0)
        prefix = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{prefix} {name} - {value}")
    return "\n".join(lines)

