import datetime
import pyrogram
from models.database import Base, TimeBase
from sqlalchemy.ext.asyncio import AsyncSession
from models import ASSession
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy import ForeignKey, String, Integer, BigInteger,Float,Numeric, CheckConstraint,DateTime,func, desc, select

class Transform(Base):
    __tablename__ = "transform"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    website: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[int] = mapped_column(BigInteger)
    bonus: Mapped[float] = mapped_column(Numeric(12, 2))


class User(TimeBase):
    __tablename__ = "user_name"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    async def get_bonus_sum_for_site(self, session: AsyncSession, site_name: str) -> float:
        bonus_sum_select = select(func.sum(Transform.bonus)).where(
            Transform.user_id == self.user_id,
            Transform.website == site_name
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0
    
    async def get_bonus_sum_for_site(self, site_name: str) -> float:
        """
        获取当前用户在指定站点的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: float
        """

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus)).where(
                Transform.user_id == self.user_id,
                Transform.website == site_name
            )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0
    
    async def get_bonus_count_sum_for_website(self, site_name: str):
    
        """
        获取当前用户在指定站点的 发送给我的 次数 、魔力总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: float
        """
        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus)).where(
                Transform.user_id == self.user_id,
                Transform.website == site_name,
                Transform.bonus > 0
            )   

        bonus_count_select = select(
            func.count()).where(
                Transform.user_id == self.user_id,
                Transform.website == site_name,
                Transform.bonus > 0
            )        
        bonus_count = (await session.execute(bonus_count_select)).scalar_one_or_none()        
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        bonus_sum = bonus_sum or 0
        bonus_count = bonus_count or 0        
        return bonus_count,bonus_sum    

    
    async def get_bonus_post_sum_for_site(self, site_name: str) -> int:
        """
        获取当前用户在指定站点的 我发送的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        """

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus)).where(
                Transform.user_id == self.user_id,
                Transform.website == site_name,
                Transform.bonus < 0
            )   
       
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return -bonus_sum if bonus_sum is not None else 0


    
    async def get_bonus_stats_by_site(self, site_name: str, top_n: int=10):
        """
        sssssss
        """

        session = ASSession()
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
        return [[i + 1, tg_id, name, count, total] for i, (tg_id, name, count, total) in enumerate(rows)]  
    
    @classmethod
    async def get(cls, tg_user: pyrogram.types.User | None, author_signature: str | None = None):
        """
        获取或创建用户记录。
        :param tg_user: 用户对象
        :type tg_user: pyrogram.types.User
        :return: 用户记录
        :rtype: User
        """

        session = ASSession()
        if tg_user:
            username = " ".join(filter(None, [tg_user.first_name, tg_user.last_name]))
            user_id = tg_user.id
        else:
            username = author_signature or "匿名用户"
            user_id = username  # 没有 TGID，只能用 author_signature 作为唯一标识

        user = await session.get(cls, user_id)
        if user:
            if user.name != username:
                user.name = username
        else:
            user = cls(user_id=user_id, name=username)
            session.add(user)
            await session.flush()
        return user
    
    async def add_transform_record(self, website: str, bonus: int):
        """
        添加转账记录。

        :param site: 站点名称
        :type site: str
        :param bonus: 转账金额
        :type bonus: int
        """
        session = ASSession()
        transform = Transform(website=website, user_id=self.user_id, bonus=bonus)
        session.add(transform)
        await session.flush()



