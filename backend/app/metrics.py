"""Pure trade math. No database access, so it is easy to unit-test."""

from collections import defaultdict
from collections.abc import Iterable

from app.models import Side, Trade


def _direction(side: Side) -> int:
    return 1 if side == Side.LONG else -1


def calc_pnl(side: Side, entry: float, exit: float | None, size: float) -> float | None:
    if exit is None:
        return None
    return (exit - entry) * size * _direction(side)


def calc_r_multiple(
    side: Side, entry: float, exit: float | None, stop: float | None
) -> float | None:
    """Result in units of initial risk: +2R means the trade made twice what it risked."""
    if exit is None or stop is None:
        return None
    risk_per_unit = abs(entry - stop)
    if risk_per_unit == 0:
        return None
    return (exit - entry) * _direction(side) / risk_per_unit


def validate_levels(
    side: Side, entry: float, stop: float | None, take_profit: float | None
) -> None:
    """Raise ValueError if stop / target sit on the wrong side of the entry."""
    if side == Side.LONG:
        if stop is not None and stop >= entry:
            raise ValueError("For a long trade the stop loss must be below the entry price")
        if take_profit is not None and take_profit <= entry:
            raise ValueError("For a long trade the take profit must be above the entry price")
    else:
        if stop is not None and stop <= entry:
            raise ValueError("For a short trade the stop loss must be above the entry price")
        if take_profit is not None and take_profit >= entry:
            raise ValueError("For a short trade the take profit must be below the entry price")


def compute_stats(trades: Iterable[Trade]) -> dict:
    trades = list(trades)
    closed = sorted(
        (t for t in trades if t.exit_price is not None),
        key=lambda t: (t.trade_date, t.id),
    )

    pnls = [calc_pnl(t.side, t.entry_price, t.exit_price, t.position_size) for t in closed]
    r_values = [
        r
        for t in closed
        if (r := calc_r_multiple(t.side, t.entry_price, t.exit_price, t.stop_loss)) is not None
    ]

    wins = sum(1 for p in pnls if p > 0)
    losses = sum(1 for p in pnls if p < 0)

    equity_curve = []
    cumulative = 0.0
    daily: dict = defaultdict(lambda: {"pnl": 0.0, "trades": 0})
    for t, pnl in zip(closed, pnls):
        cumulative += pnl
        equity_curve.append(
            {
                "trade_id": t.id,
                "date": t.trade_date,
                "symbol": t.symbol,
                "pnl": round(pnl, 2),
                "cumulative_pnl": round(cumulative, 2),
            }
        )
        daily[t.trade_date]["pnl"] += pnl
        daily[t.trade_date]["trades"] += 1

    return {
        "summary": {
            "total_trades": len(trades),
            "closed_trades": len(closed),
            "open_trades": len(trades) - len(closed),
            "wins": wins,
            "losses": losses,
            "breakeven": len(closed) - wins - losses,
            "win_rate": round(wins / len(closed) * 100, 2) if closed else None,
            "total_pnl": round(sum(pnls), 2),
            "avg_r": round(sum(r_values) / len(r_values), 2) if r_values else None,
        },
        "equity_curve": equity_curve,
        "daily_pnl": [
            {"date": d, "pnl": round(v["pnl"], 2), "trades": v["trades"]}
            for d, v in sorted(daily.items())
        ],
    }
