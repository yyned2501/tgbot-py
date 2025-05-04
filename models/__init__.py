import asyncio
import os
from models.database import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,async_scoped_session
from sqlalchemy.orm import declarative_base
from config.config import DB_INFO

if DB_INFO['dbset'] == 'SQLite':
    db_path = "sessions/tgbot.db"
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

elif DB_INFO['dbset'] == 'mySQL':
    from urllib.parse import quote_plus
    password = quote_plus(DB_INFO['password'])
    DATABASE_URL = (
        f"mysql+aiomysql://{DB_INFO['user']}:{password}"
        f"@{DB_INFO['address']}:{DB_INFO['port']}/{DB_INFO['db_name']}"
    )
async_engine = create_async_engine(DATABASE_URL, echo=True)
ASSession = async_scoped_session(
    async_sessionmaker(bind=async_engine), asyncio.current_task
)

async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)