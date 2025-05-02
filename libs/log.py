import io
import sys
import pytz
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


# 可选：东八区时间格式
class CSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        time_utc8 = datetime.fromtimestamp(record.created, pytz.timezone('Asia/Shanghai'))
        return time_utc8.strftime(datefmt or '%Y-%m-%d %H:%M:%S(%Z)')
formatter = CSTFormatter("[%(levelname)s] %(asctime)s - %(filename)s - %(message)s")
logger = logging.getLogger("Mytgbot")
logger.setLevel(logging.INFO)

# 防止重复添加 handler
"""
if not logger.handlers:    
    file_handler = RotatingFileHandler("logs/Mytgbot.log", maxBytes=10 * 1024 * 1024, backupCount=10, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)    
    utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    console_handler = logging.StreamHandler(utf8_stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
"""    

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)