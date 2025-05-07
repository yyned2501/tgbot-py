from datetime import datetime
import pyrogram
import hashlib
import unicodedata
from models.database import Base, TimeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, BigInteger,Numeric, DateTime,func, desc, select

class Transform(Base):
    __tablename__ = "transform"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    website: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[int] = mapped_column(BigInteger)
    bonus: Mapped[float] = mapped_column(Numeric(12, 2))


class User(TimeBase):
    __tablename__ = "user_name"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    async def get_bonus_sum_for_website(self, session: AsyncSession, site_name: str) -> float:
        """
        获取当前用户在指定站点的 bonus 总和。

        :param session: SQLAlchemy 异步会话
        :param site_name: 站点名称
        :return: 站点 bonus 的总和，如果不存在则返回 0
        """

        bonus_sum_select = select(func.sum(Transform.bonus)).where(
            Transform.user_id == self.user_id,
            Transform.website == site_name
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0
    


    async def get_bonus_count_sum_for_website(self, session: AsyncSession, site_name: str) -> tuple[int, float]:
        """
        获取当前用户在指定站点的 发送给我的 次数 、魔力总和。
        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: float        
        """        
        bonus_sum_select = select(func.sum(Transform.bonus)).where(
            Transform.user_id == self.user_id,
            Transform.website == site_name,
            Transform.bonus > 0
        )
        bonus_count_select = select(func.count()).where(
            Transform.user_id == self.user_id,
            Transform.website == site_name,
            Transform.bonus > 0
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none() or 0
        bonus_count = (await session.execute(bonus_count_select)).scalar_one_or_none() or 0
        
        return bonus_count, bonus_sum



    async def pay_bonus_count_sum_for_website(self, session: AsyncSession, site_name: str) -> int:
        """
        获取当前用户在指定站点的 我发送的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int        
        """
        
        bonus_sum_select = select(func.sum(Transform.bonus)).where(
            Transform.user_id == self.user_id,
            Transform.website == site_name,
            Transform.bonus < 0
        )
        bonus_count_select = select(func.count()).where(
            Transform.user_id == self.user_id,
            Transform.website == site_name,
            Transform.bonus < 0
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none() or 0
        bonus_count = (await session.execute(bonus_count_select)).scalar_one_or_none() or 0        
        return bonus_count, bonus_sum
    

    async def get_bonus_leaderboard_by_website(self,session: AsyncSession, site_name: str, Direction: str, top_n: int = 10):

        """
        sssssss
        """
        if Direction == 'pay':
            flag = Transform.bonus < 0
        else:
            flag = Transform.bonus > 0


        result_data = (
            select(
                Transform.user_id,
                User.name,
                func.count().label("bonus_count"),
                func.sum(Transform.bonus).label("bonus_sum")
            )
            .join(User, Transform.user_id == User.user_id)
            .where(
                Transform.bonus > 0,
                Transform.website == site_name
            )
            .group_by(Transform.user_id, User.name)
            .order_by(desc("bonus_sum"))
            .limit(top_n)
        )
        result = await session.execute(result_data)
        rows = result.all()
        return [
            [i + 1, tg_id, name, f"{count:,}", f"{bonus_sum:,.2f}"]
            for i, (tg_id, name, count, bonus_sum) in enumerate(rows)
        ]
        
    
    async def get_user_bonus_rank(self, session: AsyncSession, website: str) -> int:
        """
        获取当前用户在某网站上的 bonus 总和排名（降序）。
        """
        bonus_sum_stmt = (
            select(
                Transform.user_id,
                func.sum(Transform.bonus).label("total_bonus")
            )
            .where(Transform.website == website)
            .group_by(Transform.user_id)
            .order_by(desc("total_bonus"))
        )

        result = await session.execute(bonus_sum_stmt)
        rows = result.all()

        # 遍历查找当前 user_id 的排名
        for rank, (uid, _) in enumerate(rows, start=1):
            if uid == self.user_id:
                return rank
        return -1  # 没找到


   
    @classmethod
    async def get(cls, session: AsyncSession, transform_message: pyrogram.types.Message | None = None):
        if transform_message.from_user:
            tg_user = transform_message.from_user
            username = " ".join(filter(None, [tg_user.first_name, tg_user.last_name]))
            #username = clean_str_safe(username)
            user_id = tg_user.id
        else:            
            username = transform_message.author_signature or "匿名用户"
            #username = clean_str_safe(username)
            user_id = generate_user_id_from_username(username)
        user = await session.get(cls, user_id)
        if user:
            if user.name != username:
                user.name = username
        else:
            user = cls(user_id=user_id, name=username)
            session.add(user)
            await session.flush()
        return user
    
    async def add_transform_record(self, session: AsyncSession, website: str, bonus: float):
        transform = Transform(website=website, user_id=self.user_id, bonus=bonus)
        session.add(transform)
        await session.flush()

##################英文字母或者中文的拼音转ASCLL码###############################



def generate_user_id_from_username(username: str) -> int:
    #clean_name = clean_str_safe(username)
    hash_hex = hashlib.sha1(username.encode('utf-8')).hexdigest()[:20]
    return int(hash_hex, 16)  # 转为整数

##################UTF8###############################

"""
def clean_str_safe(s) -> str:
    if not isinstance(s, str):
        s = str(s)
    # 编码/解码以清除非法 surrogate
    try:
        s = s.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')
    except Exception:
        s = s.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    # 去除控制字符和不可见字符
    s = ''.join(c for c in s if unicodedata.category(c)[0] != 'C')
    # 去除无效的 Unicode 字符（替代符号、未定义、保留等）
    s = re.sub(r'[\uD800-\uDFFF]', '', s)
    # 去除不可识别的特殊字符（如某些 emoji 或 Telegram 特有字符）
    s = ''.join(c for c in s if c.isprintable())
    # 限制长度 + 去除前后空格
    return s.strip()[:100]
"""