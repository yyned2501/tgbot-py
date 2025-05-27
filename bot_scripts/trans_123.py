import subprocess
from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import MY_TGID
from libs.log import logger
from p123 import P123Client
from p123.tool import share_iterdir
from typing import List, Dict, Any


def p123_save_share(
    client: P123Client, share_key: str, share_pwd: str = "", /, parent_id: int = 0
) -> None:
    """
    将分享的文件或文件夹保存到用户的网盘中。

    Args:
        client: P123Client 实例，用于与网盘API交互。
        share_key: 分享密钥，用于标识分享链接（不能为空）。
        share_pwd: 分享密码，用于验证分享链接（默认为空字符串）。
        parent_id: 目标父文件夹ID，默认为0（根目录）。

    Raises:
        ValueError: 如果 share_key 为空。
        Exception: 如果获取文件列表或复制文件时发生错误。
    """
    # 导入工具函数，用于获取分享文件列表

    # 参数校验：确保分享密钥不为空
    if not share_key:
        raise ValueError("分享密钥不能为空")

    # 配置日志记录，用于调试和错误跟踪

    try:
        # 初始化文件列表，用于存储分享中的文件和文件夹信息
        file_list: List[Dict[str, Any]] = []

        # 获取分享链接中的文件列表
        # share_iterdir 返回分享链接中的文件信息迭代器
        for info in share_iterdir(share_key, share_pwd):
            file_list.append(info)  # 将文件信息添加到列表

        # 设置分批处理的大小，避免一次性处理过多文件导致内存占用过高
        batch_size: int = 100
        logger.info(f"总计需要处理 {len(file_list)} 个文件")

        # 分批将文件复制到网盘
        for i in range(0, len(file_list), batch_size):
            # 提取当前批次的文件列表
            batch = file_list[i : i + batch_size]
            # 调用 share_fs_copy 方法，将当前批次文件复制到目标文件夹
            client.share_fs_copy(
                {
                    "sharekey": share_key,  # 分享密钥
                    "sharepwd": share_pwd,  # 分享密码（可能为空）
                    "filelist": batch,  # 当前批次的文件列表
                },
                parent_id=parent_id,  # 目标文件夹ID
            )
            logger.info(f"成功复制 {len(batch)} 个文件到网盘")

    except Exception as e:
        # 捕获异常并记录错误详情
        logger.error(f"保存分享文件失败: {str(e)}")
        raise


def p123_save_share_link(client: P123Client, link: str, /, parent_id: int = 0) -> None:
    """
    从 123pan 分享链接中提取分享密钥和密码，并保存分享内容到网盘。

    支持无密码分享链接。如果链接包含 '?'，取最后 4 个字符作为密码；否则密码为空。

    Args:
        client: P123Client 实例，用于与网盘API交互。
        link: 123pan 分享链接（如 'https://www.123pan.com/s/PB1hTd-WOGO3' 或
              'https://www.123pan.com/s/PB1hTd-WOGO3?xxx=T2mq'）。
        parent_id: 目标父文件夹ID，默认为0（根目录）。

    Raises:
        ValueError: 如果链接无效或无法提取 share_key。
        ValueError: 如果包含 '?' 但链接过短，无法提取 4 个字符作为密码。
        Exception: 如果保存分享内容时发生错误。
    """
    from urllib.parse import urlparse

    # 配置日志记录，用于调试和错误跟踪

    try:
        # 解析分享链接
        parsed_url = urlparse(link)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("无效的分享链接格式，缺少协议或域名")

        # 提取 share_key（从路径中获取）
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 2 or path_parts[0] != "s":
            raise ValueError("分享链接格式错误，缺少分享密钥")
        share_key = path_parts[1]

        # 提取 share_pwd：如果链接包含 '?'，取最后 4 个字符；否则为空
        share_pwd = ""
        if "?" in link:
            if len(link) >= 4:
                share_pwd = link[-4:]
            else:
                raise ValueError("链接包含 '?' 但过短，无法提取 4 个字符作为密码")

        logger.info(f"提取到分享密钥: {share_key}, 密码: {share_pwd or '无'}")

        # 调用 save_share 函数处理分享内容
        p123_save_share(client, share_key, share_pwd, parent_id=parent_id)
        logger.info("分享内容保存成功")

    except Exception as e:
        # 捕获并记录异常
        logger.error(f"处理分享链接失败: {str(e)}")
        raise


@Client.on_message(
    filters.chat(MY_TGID) & filters.regex(r"https://www\.123.*?(?=\r?\n|$)")
)
async def trans_123_link(client: Client, message: Message):
    match = message.matches[0]
    url = match.group(0)
    client_123 = P123Client(passport="13809051010", password="yy920120")
    p123_save_share_link(client_123, url, parent_id=0)
    await message.reply_text("转存成功")
