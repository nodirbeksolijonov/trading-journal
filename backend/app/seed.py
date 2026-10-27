"""Fill the database with sample trades: python -m app.seed [count]"""

import random
import sys
from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Side, Trade

SYMBOLS = {"AAPL": 190, "TSLA": 240, "NVDA": 120, "SPY": 520, "BTCUSD": 65000}
STRATEGIES = ["breakout", "pullback", "reversal", "range"]
EMOTIONS = ["calm", "confident", "anxious", "fomo", "greedy", "fearful", "frustrated", "neutral"]


def make_trade(day: date) -> Trade:
    symbol, base = random.choice(list(SYMBOLS.items()))
    side = random.choice(list(Side))
    entry = round(base * random.uniform(0.95, 1.05), 2)
    risk = entry * random.uniform(0.005, 0.02)
    direction = 1 if side == Side.LONG else -1
    stop = round(entry - direction * risk, 2)
    target = round(entry + direction * risk * 2, 2)
    # Outcome in R: slightly positive edge, losers mostly capped at -1R.
    outcome_r = random.choice([-1, -1, -1, -0.5, 0, 0.5, 1, 2, 2, 3])
    exit_price = round(entry + direction * risk * outcome_r, 2)
    size = round(1000 / risk, 4) if symbol != "BTCUSD" else round(100 / risk, 4)
    return Trade(
        symbol=symbol,
        side=side,
        entry_price=entry,
        exit_price=exit_price,
        position_size=size,
        stop_loss=stop,
        take_profit=target,
        trade_date=day,
        strategy=random.choice(STRATEGIES),
        notes="Sample trade",
        emotion_before=random.choice(EMOTIONS),
        emotion_after=random.choice(EMOTIONS),
    )


def main(count: int = 60) -> None:
    Base.metadata.create_all(bind=engine)
    start = date.today() - timedelta(days=90)
    with SessionLocal() as db:
        for _ in range(count):
            db.add(make_trade(start + timedelta(days=random.randint(0, 90))))
        db.commit()
    print(f"Inserted {count} sample trades")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
