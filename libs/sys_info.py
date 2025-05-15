import os
import sys
import platform
import pyrogram

async def system_version_get():
    sys_info = platform.uname()
    project_name = os.path.basename(os.path.abspath(os.curdir))
    python_info = f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    pyrogram_info = f"脚本依赖: pyrogram: {pyrogram.__version__}" 
    re_message = f"您的`{project_name}`项目在`{sys_info.node}`的`{sys_info.system}`设备上登录 \n{python_info} {pyrogram_info}"
    return re_message