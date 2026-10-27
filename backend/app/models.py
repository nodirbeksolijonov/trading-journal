import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Side(str, enum.Enum):
    LONG = "long"
    SHORT = "short"


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[Side] = mapped_column(
        Enum(Side, native_enum=False, length=5, values_callable=lambda e: [m.value for m in e])
    )
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[float | None] = mapped_column(Float)  # None = trade still open
    position_size: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float | None] = mapped_column(Float)
    take_profit: Mapped[float | None] = mapped_column(Float)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    strategy: Mapped[str | None] = mapped_column(String(50), index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    emotion_before: Mapped[str | None] = mapped_column(String(30))
    emotion_after: Mapped[str | None] = mapped_column(String(30))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
