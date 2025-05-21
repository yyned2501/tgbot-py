import os
from libs import others
from config import config
from libs.log import logger
from models import async_session_maker
from models.transform_db_modle import User
from sqlalchemy.ext.asyncio import AsyncSession
from pyrogram.types.messages_and_media import Message
from libs.leaderboard_imge import get_leaderboard

async def transform(transform_message: Message, bonus: int, website: str, bonus_name: str,leaderboard: bool = True):    
    async with async_session_maker() as session:
        async with session.begin():
            try:
                user = await User.get(session, transform_message)
                await user.add_transform_record(session, website, bonus)
                get_count, get_bonus = await user.get_bonus_count_sum_for_website(session, website)
                pay_count, pay_bonus = await user.pay_bonus_count_sum_for_website(session, website)
                if leaderboard:       
                    leaderboard_top5 = await user.get_bonus_leaderboard_by_website(session=session, site_name=website, Direction="get", top_n=5)
                    user_ranking = await user.get_user_bonus_rank(session, website)
                    leaderboard_top5_imge = await get_leaderboard(leaderboard_top5)
                                
            except Exception as e:
                logger.exception(f"提交失败: 用户消息：{transform_message}, 错误：{e}")
                await transform_message.reply("转换失败，请稍后再试。") 
        if leaderboard:
            re_mess = await transform_message.reply_photo(
                photo = leaderboard_top5_imge,

                caption =f"```"
                f"\n{user.name} 大佬，感谢您打赏的{bonus} {bonus_name}\n"
                f"您打赏了小弟{get_count}次，共计{get_bonus} {bonus_name}\n"
                f"您是{config.MY_NAME}哥个人打赏总榜的第 {user_ranking} 名\n"
                f"当前{config.MY_NAME}哥个人打赏总榜TOP5如图上所示\n"
                f"```"
            )        
            os.remove(leaderboard_top5_imge)
            await others.delete_message(re_mess,30)
       

           
