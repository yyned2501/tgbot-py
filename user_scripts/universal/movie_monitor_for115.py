import re
import json
import shutil
import aiohttp
from pathlib import Path
from libs.log import logger
from aiohttp import ClientTimeout
from typing import List, Optional
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from config.config import GROUP_ID, ADMIN_ID, EMBY_API_KEY, EMBY_SERVER,TMDB_API_KEY,proxy_set,CMS_trans


media_path = Path("data/get_media")
monitor_enabled = True
LINK_PATTERN = re.compile(r"https://115cdn\.com/s/[^\s]+")  # 匹配 115 链接

 
# ================== TMDB API 类 ==================
class TmdbApi:
    """
    TMDB识别匹配（异步版）
    """
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.language = 'zh'
        self.base_url = 'https://api.themoviedb.org/3'
        self.proxy = proxy_set['PROXY_URL']  # 可以是 socks5 或 http 代理

    def _get_request_kwargs(self, params: dict) -> dict:
        """构造 aiohttp 请求参数，是否使用代理由 proxy_enable 决定"""
        kwargs = {
            'params': params,
            'ssl': False
        }
        if proxy_set['proxy_enable'] == True:
            kwargs['proxy'] = self.proxy
        return kwargs

    async def search_all(self, title: str, year: str = None) -> List[dict]:
        """
        异步搜索电影和电视剧，返回带有类型字段的结果
        """
        movie_results = await self.search_movies(title, year)
        tv_results = await self.search_tv(title, year)
        for result in movie_results:
            result["media_type"] = "movie"
        for result in tv_results:
            result["media_type"] = "tv"

        return movie_results + tv_results
    
    async def search_movies(self, title: str, year: str = None) -> List[dict]:
        """异步查询电影"""
        if not title:
            return []

        url = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'language': self.language,
            'query': title,
            'year': year
        }

        try:
            timeout = ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                kwargs = self._get_request_kwargs(params)
                async with session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get('results', [])
        except aiohttp.ClientError as e:
            logger.error(f"TMDB Movie API 错误: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"其他错误: {str(e)}")
            return []
        

    async def search_tv(self, title: str, year: str = None) -> List[dict]:
        """异步查询电视剧"""
        if not title:
            return []

        url = f"{self.base_url}/search/tv"
        params = {
            'api_key': self.api_key,
            'language': self.language,
            'query': title,
            'first_air_date_year': year
        }

        try:
            timeout = ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                kwargs = self._get_request_kwargs(params)
                async with session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get('results', [])
        except aiohttp.ClientError as e:
            logger.error(f"TMDB TV API 错误: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"其他错误: {str(e)}")
            return []

    @staticmethod
    def compare_names(file_name: str, tmdb_names: list) -> bool:
        """比较文件名是否匹配，忽略大小写和特殊字符"""
        if not file_name or not tmdb_names:
            return False
        if not isinstance(tmdb_names, list):
            tmdb_names = [tmdb_names]
        file_name = re.sub(r'[\W_]+', ' ', file_name).strip().upper()
        for tmdb_name in tmdb_names:
            tmdb_name = re.sub(r'[\W_]+', ' ', tmdb_name).strip().upper()
            if file_name == tmdb_name:
                return True
        return False
    

async def get_movies(title: str, year: Optional[str] = None, tmdb_id: Optional[int] = None):
    """
    根据标题和年份，检查电影是否在Emby中存在，存在则返回列表
    :param title: 标题
    :param year: 年份，可以为空，为空时不按年份过滤
    :param tmdb_id: TMDB ID
    :param host: 媒体服务器的主机地址
    :param apikey: API 密钥
    :return: 含title、year属性的字典列表
    """      
    url = f"{EMBY_SERVER}emby/Items"
    params = {
        "IncludeItemTypes": "Movie",
        "Fields": "ProviderIds,OriginalTitle,ProductionYear,Path,UserDataPlayCount,UserDataLastPlayedDate,ParentId",
        "StartIndex": 0,
        "Recursive": "true",
        "SearchTerm": title,
        "Limit": 10,
        "IncludeSearchTypes": "false",
        "api_key": EMBY_API_KEY
    }

    try:
        # 使用 aiohttp 异步请求
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                res = await response.json()                
                if res:
                    res_items = res.get("Items")
                    if res_items:
                        tmdb_values = []
                        tmdb_values = [item['ProviderIds'].get('Tmdb') for item in res_items if 'Tmdb' in item['ProviderIds']]                        
                        return tmdb_values
                    else:
                        return []
                else:
                    return []                    
    except Exception as e:
        logger.error(f"连接Items出错：" + str(e))
        return []

       
        
# ================== 消息处理逻辑 ==================

async def extract_115_links(message: Message) -> List[str]:
    """提取消息中的 115 链接"""
    if message.caption:
        return LINK_PATTERN.findall(message.caption)
    return []


async def send_115_links(client:Client, message, title, year):
    """
    提取并发送 115 链接
    """
    links = await extract_115_links(message)
    if links:
        for link in links:
            await client.send_message(GROUP_ID['CMS_BOT_ID'], link)
            logger.info(f"已发送媒体: [标题: {title}, 年份: {year}] 链接: {link}")
    else:
        logger.warning("未找到 115 链接。")
        

async def search_and_send_message(client:Client, title, year,message):
        if title:
            # 使用 TMDB API 匹配电影
            tmdb_api = TmdbApi()
            results = await tmdb_api.search_all(title, year)            
            if results:
                full_match = next(
                    (
                        i for i, item in enumerate(results)
                        if (item.get("title") == title or item.get("name") == title)
                        and ((item.get("release_date") or item.get("first_air_date") or "")[:4] == str(year))
                    ),
                    None
                )
                if full_match is None:
                    a_only_match = next(
                        (
                            i for i, item in enumerate(results)
                            if item.get("title") == title or item.get("name") == title
                        ),
                        None
                    )
                    result_index = a_only_match if a_only_match is not None else 0
                else:
                    result_index = full_match                                  
                tmdb_title = results[result_index].get('title') or results[result_index].get('name', '未知标题')                
                tmdb_year =  results[result_index].get('release_date') or results[result_index].get('first_air_date',"未知时间") 
                tmdb_id = results[result_index].get('id','未知ID')
                tmdb_media_type = results[result_index].get('media_type',"未知类型")
                logger.info(f":TMDB已匹配媒体：[标题: {tmdb_title}, 上映时间: {tmdb_year}, Movie_id: {tmdb_id}, media_type: {tmdb_media_type}]")
                if tmdb_media_type == 'movie':
                    # 检查 EMBY 媒体库是否已存在该电影
                    try:
                        tmdb_list = await get_movies(title=title, year=year)
                        if tmdb_list:
                            if str(tmdb_id) not in tmdb_list:
                                await send_115_links(client, message, title, year)
                            else:
                                logger.info(f"媒体库已存在该电影 | 标题: {title}, TMDB-ID: {tmdb_id}")
                        else:
                            await send_115_links(client, message, title, year)
                    except Exception as e:
                        logger.error(f"获取电影信息失败: {str(e)}")
                else:
                    logger.info(f"媒体类型不为电影 | 标题: {title}, TMDB-ID: {tmdb_id}")
        else:
            logger.info(f"TMDB未匹配到媒体 | 标题: {title}, 年份: {year}")


@Client.on_message(
        (filters.chat(GROUP_ID["CHANNEL_SHARES_115_ID"])
         | filters.chat(GROUP_ID["PAN115_SHARE_ID"])
         | filters.chat(GROUP_ID['GUAGUALE115_ID']))
         & filters.regex(r"https://115cdn\.com/s/[^\s]+")
         )
async def monitor_channels(client: Client, message: Message):
    """监控频道消息，提取并转发 115 链接。"""
    global monitor_enabled
    title = ""
    if not monitor_enabled:
        return
    
    # 判断是否为电影消息    
    if (message.chat.id == GROUP_ID["CHANNEL_SHARES_115_ID"]
        or message.chat.id == GROUP_ID["GUAGUALE115_ID"]):
        match = None
        caption = message.caption or "" 
        match = re.search(r"(.*?)\s*\((\d+)\)", caption)         
        if match:
            title = match.group(1).strip()  # 括号前的内容
            year = match.group(2).strip()   
              
        
    elif message.chat.id == GROUP_ID["PAN115_SHARE_ID"]:
        
        match = None
        caption = message.caption or "" 
             
        if "】" in message.caption:
            pattern = r"[】](.*?)\s*\((\d+)\)"
        else:  # 如果没有【】，从:后匹配
            pattern = r"[:] (.*?)\s*\((\d+)\)"

        match = re.search(pattern, caption) 
        if match:
            title = match.group(1).strip()  # 括号前的内容
            year = match.group(2).strip() 
    if title and year:        
        logger.info(f"检索到群组: [{message.chat.title}] 媒体信息: {title} {year}")
        await search_and_send_message(client,title, year,message)




# ================== 开关命令处理 ==================
@Client.on_message(
        filters.me 
        & filters.command("dyjk")
    )
async def toggle_monitor(client: Client, message: Message):
    """切换监控功能状态"""
    global monitor_enabled

    parts = message.text.split()
    command = parts[1].lower() if len(parts) > 1 else ""

    if command in ("on", "off"):
        monitor_enabled = (command == "on")
        status = "启动" if monitor_enabled else "停止"
        await message.reply(f"监控功能已{status}！")
    else:
        await message.reply("无效命令。请使用 `/dyjk on` 或 `/dyjk off`。")


@Client.on_message(
        filters.private 
        & filters.user(GROUP_ID['CMS_BOT_ID'])
    )
async def forward_to_group(client:Client, message: Message):
    """
    CMS_BOT message 转发 给个人CMS群组
    """
    if CMS_trans == True:
        await message.copy(GROUP_ID['CMS_TRANS_CHAT'])
        logger.info(f"成功将CMS_BOT的消息转发给个人CMS群组")


@Client.on_message(
        filters.chat(GROUP_ID['CMS_TRANS_CHAT'])
        & filters.user(ADMIN_ID)
    )

async def forward_to_CMS_bot(client:Client, message: Message):
    """
    个人CMS群组的特定人员消息转发至CMS_BOT
    """

    if CMS_trans == True:
        await message.copy(GROUP_ID['CMS_BOT_ID'])
        logger.info(f"成功将群组消息转发给CMS_BOT")




# ================== 手动查询媒体信息 ==================
@Client.on_message(
    filters.me & filters.command("getmedia")
)
async def getmedia(client: Client, message: Message):
    media_path.mkdir(parents=True, exist_ok=True)

    args = message.command[1:]
    title = args[0] if len(args) >= 1 else ""
    year = args[1] if len(args) >= 2 else "0"

    if not title:
        await message.reply("请提供电影名称，例如：/getmedia 泰坦尼克号 1997")
        return

    tmdb_api = TmdbApi()
    result_mess = await tmdb_api.search_all(title, year)
    
    file_path = media_path / f"{title}({year}).txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(result_mess, ensure_ascii=False, indent=4))

    await client.send_document(GROUP_ID['MESSAGE_TRASN_CHAT'], file_path)
    shutil.rmtree("data/get_media", ignore_errors=True)
    await message.delete()