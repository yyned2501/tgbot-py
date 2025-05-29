from pyrogram import filters, Client
from pyrogram.types import Message

from config.config import MY_TGID
from libs.state import state_manager
from schedulers import scheduler
from schedulers.zhuque.fireGenshinCharacterMagic import zhuque_autofire_firsttimeget


@Client.on_message(filters.chat(MY_TGID) & filters.command("scheduler_jobs"))
async def zhuque_fanda_switch(client: Client, message: Message):
    jobs = scheduler.get_jobs()
    if not jobs:
        await message.reply("当前没有正在运行的调度任务。")
    else:
        job_list = "\n".join([f"- {job.id}" for job in jobs])
        await message.reply(f"当前运行的调度任务有：\n{job_list}")


@Client.on_message(filters.chat(MY_TGID) & filters.command("autofire"))
async def zhuque_autofire_switch(client: Client, message: Message):
    """
    自动释放技能开关监听
    用法：/autofire on | off
    """
    if len(message.command) < 2:
        await message.reply("❌ 参数不足。\n用法：`/autofire on|off`")
        return
    action = message.command[1].lower()
    valid_modes = {"on", "off"}

    if action not in valid_modes:
        await message.reply("❌ 参数非法。\n有效选项：`on` `off`")
        return
    state_manager.set_section("SCHEDULER", {"autofire": action})
    if action == "off":
        await message.reply("🛑 自动释放技能已关闭")
        scheduler.remove_job("firegenshin")
    else:
        await message.reply(f"✅ 自动释放技能模式 `{action}` 已开启")
        await zhuque_autofire_firsttimeget()
