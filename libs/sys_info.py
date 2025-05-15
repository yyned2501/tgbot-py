
import sys
import platform
import pyrogram

async def system_version_get():
    sys_info = platform.uname()
    python_info = f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    pyrogram_info = f"脚本依赖: pyrogram: {pyrogram.__version__}"
    re_message1 = f"{sys_info.node} 的 {sys_info.system} 设备"
    re_message2 = f"{python_info} {pyrogram_info}"
    return re_message1,re_message2
