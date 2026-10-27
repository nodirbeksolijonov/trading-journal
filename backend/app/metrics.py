"""Pure trade math. No database access, so it is easy to unit-test."""

from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import date

from app.models import Side, Trade


def round2(value: float) -> float:
    # Adding 0.0 turns -0.0 (e.g. round(-0.001, 2)) into 0.0 so clients never show "-$0.00".
    return round(value, 2) + 0.0


def _direction(side: Side) -> int:
    return 1 if side == Side.LONG else -1


def calc_pnl(
    side: Side, entry: float, exit: float | None, size: float, fees: float = 0
) -> float | None:
    """Net P&L: price move times size, minus fees."""
    if exit is None:
        return None
    return (exit - entry) * size * _direction(side) - fees


def calc_r_multiple(
    side: Side,
    entry: float,
    exit: float | None,
    stop: float | None,
    size: float,
    fees: float = 0,
) -> float | None:
    """Net P&L in units of initial risk: +2R means the trade made twice what it risked."""
    if exit is None or stop is None:
        return None
    risk = abs(entry - stop) * size
    if risk == 0:
        return None
    return calc_pnl(side, entry, exit, size, fees) / risk


def validate_exit(exit_price: float | None, entry_date: date, exit_date: date | None) -> None:
    """Raise ValueError unless exit price and exit date are given together, in order."""
    if exit_price is not None and exit_date is None:
        raise ValueError("Exit date is required when the trade has an exit price")
    if exit_price is None and exit_date is not None:
        raise ValueError("Exit date needs an exit price (leave both empty for an open trade)")
    if exit_date is not None and exit_date < entry_date:
        raise ValueError("Exit date can't be before the entry date")


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


def _performance(rows: list[tuple[Trade, float, float | None]]) -> dict:
    wins = sum(1 for _, pnl, _ in rows if pnl > 0)
    r_values = [r for _, _, r in rows if r is not None]
    return {
        "trades": len(rows),
        "wins": wins,
        "win_rate": round2(wins / len(rows) * 100) if rows else None,
        "total_pnl": round2(sum(pnl for _, pnl, _ in rows)),
        "avg_r": round2(sum(r_values) / len(r_values)) if r_values else None,
    }


def _breakdown(
    rows: list[tuple[Trade, float, float | None]], label_of: Callable[[Trade], str | None]
) -> list[dict]:
    """Group closed trades by a tag (case-insensitive), best total P&L first."""
    groups: dict[str | None, dict] = {}
    for row in rows:
        label = label_of(row[0])
        key = label.lower() if label else None
        groups.setdefault(key, {"label": label, "rows": []})["rows"].append(row)
    result = [{"key": g["label"], **_performance(g["rows"])} for g in groups.values()]
    return sorted(result, key=lambda g: g["total_pnl"], reverse=True)


def trade_pnl(t: Trade) -> float | None:
    return calc_pnl(t.side, t.entry_price, t.exit_price, t.position_size, t.fees)


def trade_r(t: Trade) -> float | None:
    return calc_r_multiple(t.side, t.entry_price, t.exit_price, t.stop_loss, t.position_size, t.fees)


def compute_stats(trades: Iterable[Trade]) -> dict:
    trades = list(trades)
    # P&L is realised on the exit date, so the curve and calendar are ordered by it.
    closed = sorted(
        (t for t in trades if t.exit_price is not None),
        key=lambda t: (t.exit_date, t.id),
    )
    rows = [(t, trade_pnl(t), trade_r(t)) for t in closed]

    overall = _performance(rows)
    losses = sum(1 for _, pnl, _ in rows if pnl < 0)

    equity_curve = []
    cumulative = 0.0
    daily: dict = defaultdict(lambda: {"pnl": 0.0, "trades": 0})
    for t, pnl, _ in rows:
        cumulative += pnl
        equity_curve.append(
            {
                "trade_id": t.id,
                "date": t.exit_date,
                "symbol": t.symbol,
                "pnl": round2(pnl),
                "cumulative_pnl": round2(cumulative),
            }
        )
        daily[t.exit_date]["pnl"] += pnl
        daily[t.exit_date]["trades"] += 1

    return {
        "summary": {
            "total_trades": len(trades),
            "closed_trades": len(closed),
            "open_trades": len(trades) - len(closed),
            "wins": overall["wins"],
            "losses": losses,
            "breakeven": len(closed) - overall["wins"] - losses,
            "win_rate": overall["win_rate"],
            "total_pnl": overall["total_pnl"],
            "total_fees": round2(sum(t.fees for t in closed)),
            "avg_r": overall["avg_r"],
        },
        "equity_curve": equity_curve,
        "daily_pnl": [
            {"date": d, "pnl": round2(v["pnl"]), "trades": v["trades"]}
            for d, v in sorted(daily.items())
        ],
        "by_strategy": _breakdown(rows, lambda t: t.strategy),
        "by_emotion_before": _breakdown(rows, lambda t: t.emotion_before),
        "by_emotion_after": _breakdown(rows, lambda t: t.emotion_after),
    }
