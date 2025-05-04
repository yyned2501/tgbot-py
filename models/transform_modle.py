import datetime
import pyrogram
from models.database import Base, TimeBase
from models import ASSession
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy import ForeignKey, String, Integer, BigInteger,Float,Numeric, CheckConstraint,DateTime,func, select

class User(TimeBase):
    __tablename__ = "USER_NAME"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    
    """
    async def get_bonus_sum_for_site(self, site_name: str) -> int:
        
        获取当前用户在指定站点的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus).filter(
                Transform.user_id == self.id, Transform.site == site_name
            )
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0
    
    async def get_bonus_get_sum_for_site(self, site_name: str) -> int:
        
        获取当前用户在指定站点的 发送给我的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus).filter(
                Transform.user_id == self.id,
                Transform.site == site_name,
                Transform.bonus > 0,
            )
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0
    
    async def get_bonus_post_sum_for_site(self, site_name: str) -> int:
        
        获取当前用户在指定站点的 我发送的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus).filter(
                Transform.user_id == self.id,
                Transform.site == site_name,
                Transform.bonus < 0,
            )
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return -bonus_sum if bonus_sum is not None else 0
    """
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
            user = cls(id=user_id, name=username)
            session.add(user)
            await session.flush()
        return user
    
    async def add_transform_record(self, site: str, bonus: int):
        """
        添加转账记录。

        :param site: 站点名称
        :type site: str
        :param bonus: 转账金额
        :type bonus: int
        """
        session = ASSession()
        transform = Transform(website=site, user_id=self.id, bonus=bonus)
        session.add(transform)
        await session.flush()


class Transform(Base):
    __tablename__ = "transform"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    website: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[int] = mapped_column(BigInteger)
    bonus: Mapped[float] = mapped_column(Numeric(12, 2))
