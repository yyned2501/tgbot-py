import os
from libs import others
from config import config
from models.transform_modle import User
from sqlalchemy.ext.asyncio import AsyncSession
from pyrogram.types.messages_and_media import Message
from libs.leaderboard.leaderboard_imge import get_leaderboard

async def transform(session: AsyncSession, transform_message: Message, bonus: int, website: str, bonus_name: str,leaderboard: bool = True):     
    
    user = await User.get(session, transform_message)
    await user.add_transform_record(session, website, bonus)
    
    # 获取统计数据
    get_count, get_bonus = await user.get_bonus_count_sum_for_website(session, website)
    pay_count, pay_bonus = await user.pay_bonus_count_sum_for_website(session, website)

    if leaderboard:       
        leaderboard_top5 = await user.get_bonus_leaderboard_by_website(session, website,3)
        user_ranking = await user.get_user_bonus_rank(session, website)
        leaderboard_top5_imge = await get_leaderboard(leaderboard_top5)
        await transform_message.reply_photo(
            photo = leaderboard_top5_imge,

            caption =f"```"
            f"{user.name} 大佬，感谢您打赏的{bonus} {bonus_name}\n"
            f"您打赏了小弟{get_count}次，共计{get_bonus} {bonus_name}\n"
            f"您是{config.MY_NAME}哥个人打赏总榜的第 {user_ranking} 名\n"
            f"当前{config.MY_NAME}哥个人打赏总榜TOP5如图上所示\n"
            f"```"
        )        
        os.remove(leaderboard_top5_imge)


        """
            if bonus > 0:
                reply_message = (
                    f"```\n感谢 {user.name} 大佬赠送的 {bonus} {bonus_name}\n"
                    f"大佬一共给小弟转了 {get_bonus} {bonus_name}\n"
                    f"小弟一共给大佬转了 {post_bonus} {bonus_name}\n"
                    "```"
                )
            else:
                reply_message = (
                    f"```\n小{user.name}, 送你 {-bonus} {bonus_name} 能不能让你叫我一声大佬？\n"
                    f"我一共给你转了 {post_bonus} {bonus_name}\n"
                    "```"
                )
   """
           
