
from libs import others
from models.database import Base
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, Numeric, DateTime,func, select

class Redpocket(Base):
    __tablename__ = "redpocket"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    website: Mapped[str] = mapped_column(String(32))
    gamemode: Mapped[str] = mapped_column(String(32))    
    bonus: Mapped[float] = mapped_column(Numeric(12, 2))

    @classmethod     
    async def add_redpocket_record(cls, session: AsyncSession, website: str, gamemode: str, bonus: float):
        redpocket = cls(website=website, gamemode=gamemode, bonus=bonus)
        session.add(redpocket)
        await session.flush()

    @classmethod 
    async def get_bonus_redpocket_for_website(
        cls,
        session: AsyncSession,
        website: str,
        gamemode: str, 
    ) -> float:
        """
        获取当前指定站点,指定mode bonus 的总和。        
        website: 站点名称
        :return: 站点 bonus 的总和，如果不存在则返回 0
        """
        bonus_sum_select = select(func.sum(cls.bonus)).where(
            cls.website == website,
            cls.gamemode == gamemode
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0    

    @classmethod
    async def get_bonus_count_sum_redpocket_for_website(
        cls,
        session: AsyncSession,
        website: str,
        gamemode: str,
        Direction: str,
        start_date = None,
        end_date = None,
    ) -> tuple[int, float]:
        """
        获取指定站点的 红包、次数 和 >0 的总和。
        :param website: 站点名称
        :type website: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: float 
        
        获取指定站点与模式下，指定时间范围内的红包总次数与奖金。
        - 如果不传 start_date 和 end_date，则查询全部数据。
        - 如果只传一个日期，则视为当天。
             
        """ 
        conditions = [
            cls.website == website,
            cls.gamemode == gamemode,            
        ]
        if Direction == 'pay':
            conditions.append(cls.bonus < 0)
        elif Direction == 'get':
            conditions.append(cls.bonus > 0)

        # 时间过滤逻辑
        if start_date or end_date:
            start = others.parse_date_input(start_date or end_date)
            end = others.parse_date_input(end_date or start_date)
            # 若为同一天，则 end 向后推一天以覆盖整天
            if start.date() == end.date():
                end += timedelta(days=1)
            conditions.extend([
                cls.create_time >= start,
                cls.create_time < end
            ])
        bonus_sum_stmt = select(func.sum(cls.bonus)).where(conditions)
        bonus_count_stmt = select(func.count()).where(conditions)
        # 执行查询
        bonus_sum = (await session.execute(bonus_sum_stmt)).scalar_one_or_none() or 0
        bonus_count = (await session.execute(bonus_count_stmt)).scalar_one_or_none() or 0
        return bonus_count, float(bonus_sum)