from enum import Enum
import pyrogram
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
)
from app import get_bot_app
import logging

logger = logging.getLogger("main")

ADMINS: dict[str, pyrogram.types.User] = {}


class CommandScope(Enum):
    PRIVATE_CHATS = BotCommandScopeAllPrivateChats()


BOT_COMMANDS: list[tuple[BotCommand, list[CommandScope]]] = [
    (
        BotCommand("helpme", "查看帮助信息"),
        [CommandScope.PRIVATE_CHATS],
    ),
]


async def setup_commands():
    bot_app = get_bot_app()
    scopes_dict: dict[str, list[BotCommand]] = {
        scope.name: [] for scope in CommandScope
    }
    # 清除旧命令
    await bot_app.delete_bot_commands()

    # 添加新命令
    logger.info("正在设置命令...")
    for scope, commands in scopes_dict.items():
        try:
            await bot_app.set_bot_commands(commands, scope=CommandScope[scope].value)
        except Exception as e:
            logger.error(f"设置命令失败: {e}")
