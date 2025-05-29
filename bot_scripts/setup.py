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
    (
        BotCommand("update", "更新机器人"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("fanda", "朱雀自动反打开关"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("fanxian", "朱雀自动打劫返现开关"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("autofire", "朱雀自动释放技能开关"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("lotterysw", "小菜自动参与抽奖开关"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("lotteryuser", "魔力类中奖领奖用PT站点用户名"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("lotterytime", "小菜自动参与抽奖时间段"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("autochangename", "自动修改报时昵称"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("state", "查看当前状态参数"),
        [CommandScope.PRIVATE_CHATS],
    ),
    (
        BotCommand("scheduler_jobs", "查询定时任务"),
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
    for cmd, scopes in BOT_COMMANDS:
        for scope in scopes:
            scopes_dict[scope.name].append(cmd)
    logger.info("正在设置命令...")
    for scope, commands in scopes_dict.items():
        try:
            logger.info(f"设置命令: {scope}, {commands}")
            await bot_app.set_bot_commands(commands, scope=CommandScope[scope].value)
        except Exception as e:
            logger.error(f"设置命令失败: {e}")
