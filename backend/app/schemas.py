from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.metrics import calc_pnl, calc_r_multiple, round2, validate_exit, validate_levels
from app.models import Side


class TradeBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    side: Side
    entry_price: float = Field(gt=0)
    exit_price: float | None = Field(default=None, gt=0)
    position_size: float = Field(gt=0)
    stop_loss: float | None = Field(default=None, gt=0)
    take_profit: float | None = Field(default=None, gt=0)
    fees: float = Field(default=0, ge=0)  # commissions, swaps etc. for the whole trade
    entry_date: date
    exit_date: date | None = None
    strategy: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=5000)
    emotion_before: str | None = Field(default=None, max_length=30)
    emotion_after: str | None = Field(default=None, max_length=30)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, v):
        return v.strip().upper() if isinstance(v, str) else v

    @field_validator("strategy", "notes", "emotion_before", "emotion_after", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @field_validator("fees", mode="before")
    @classmethod
    def null_fees_to_zero(cls, v):
        return 0 if v is None else v

    @model_validator(mode="after")
    def check_levels(self):
        validate_exit(self.exit_price, self.entry_date, self.exit_date)
        validate_levels(self.side, self.entry_price, self.stop_loss, self.take_profit)
        return self


class TradeCreate(TradeBase):
    pass


class TradeRead(TradeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def gross_pnl(self) -> float | None:
        pnl = calc_pnl(self.side, self.entry_price, self.exit_price, self.position_size)
        return None if pnl is None else round2(pnl)

    @computed_field
    @property
    def pnl(self) -> float | None:
        """Net of fees."""
        pnl = calc_pnl(self.side, self.entry_price, self.exit_price, self.position_size, self.fees)
        return None if pnl is None else round2(pnl)

    @computed_field
    @property
    def r_multiple(self) -> float | None:
        r = calc_r_multiple(
            self.side, self.entry_price, self.exit_price, self.stop_loss, self.position_size, self.fees
        )
        return None if r is None else round2(r)


class StatsSummary(BaseModel):
    total_trades: int
    closed_trades: int
    open_trades: int
    wins: int
    losses: int
    breakeven: int
    win_rate: float | None  # percent, None when there are no closed trades
    total_pnl: float  # net of fees
    total_fees: float
    avg_r: float | None


class EquityPoint(BaseModel):
    trade_id: int
    date: date  # exit date
    symbol: str
    pnl: float
    cumulative_pnl: float


class DailyPnl(BaseModel):
    date: date
    pnl: float
    trades: int


class GroupPerformance(BaseModel):
    key: str | None  # None = trades without this tag
    trades: int
    wins: int
    win_rate: float | None
    total_pnl: float
    avg_r: float | None


class Stats(BaseModel):
    summary: StatsSummary
    equity_curve: list[EquityPoint]
    daily_pnl: list[DailyPnl]
    by_strategy: list[GroupPerformance]
    by_emotion_before: list[GroupPerformance]
    by_emotion_after: list[GroupPerformance]
