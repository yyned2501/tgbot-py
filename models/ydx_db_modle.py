from models.database import Base
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, Numeric, DateTime, func, desc, select
from models import async_session_maker


class Zhuqueydx(Base):
    """
    朱雀ydx 数据库
    """

    __tablename__ = "zhuque_ydx"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    website: Mapped[str] = mapped_column(String(32))
    die_point: Mapped[int] = mapped_column(Integer)
    lottery_result: Mapped[str] = mapped_column(String(32))
    high_count: Mapped[int] = mapped_column(Integer)
    bet_amount: Mapped[float] = mapped_column(Numeric(16, 2))
    win_amount: Mapped[float] = mapped_column(Numeric(16, 2))

    @classmethod
    async def add_zhuque_ydx_result_record(
        cls,
        website: str,
        die_point: int,
        lottery_result: str,
        high_count: int,
        bet_amount: float,
        win_amount: float,
    ):
        """
        ydx数据写入数据库

        参数:
            website (str): 网站名称
            die_point (int): 死点
            lottery_result (str): 开奖结果
            high_count (int): 高点数
            bet_amount (float): 投注金额
            win_amount (float): 中奖金额

        返回:
            None
        """
        async with async_session_maker() as session, session.begin():
            redpocket = cls(
                website=website,
                die_point=die_point,
                lottery_result=lottery_result,
                high_count=high_count,
                bet_amount=bet_amount,
                win_amount=win_amount,
            )
            session.add(redpocket)
