
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config.config import DB_INFO
from models.database import Base

# SQLite配置路径
db_path = "sessions/tgbot.db"
db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# 根据配置选择数据库
if DB_INFO['dbset'] == 'SQLite':
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

elif DB_INFO['dbset'] == 'mySQL':
    from urllib.parse import quote_plus
    password = quote_plus(DB_INFO['password'])
    DATABASE_URL = (
        f"mysql+aiomysql://{DB_INFO['user']}:{password}"
        f"@{DB_INFO['address']}:{DB_INFO['port']}/{DB_INFO['db_name']}"
    )

# SQLite 和 MySQL 的连接配置
if DB_INFO['dbset'] == 'SQLite':
    # SQLite 不使用连接池
    async_engine = create_async_engine(DATABASE_URL, echo=True)
    

else:
    # MySQL 使用连接池
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_size=10,  # MySQL 使用连接池
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
    )

# 创建 sessionmaker
async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)

async def create_all():
    async with async_engine.begin() as conn:
        if DB_INFO['dbset'] == 'SQLite':
            await conn.execute(text("PRAGMA journal_mode=WAL;"))
            await conn.execute(text("PRAGMA synchronous=OFF;"))
        await conn.run_sync(Base.metadata.create_all)