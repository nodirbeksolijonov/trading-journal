def test_empty_stats(client):
    s = client.get("/api/stats").json()
    assert s["summary"]["win_rate"] is None
    assert s["summary"]["total_pnl"] == 0
    assert s["equity_curve"] == []


def test_stats_summary_curve_and_calendar(client, make_trade):
    make_trade(trade_date="2026-10-01", exit_price=110)  # +100, +2R
    make_trade(trade_date="2026-10-01", exit_price=95)  # -50, -1R
    make_trade(trade_date="2026-10-02", side="short", stop_loss=105, take_profit=85, exit_price=90)  # +100, +2R
    make_trade(trade_date="2026-10-03", exit_price=None)  # open, ignored in stats

    s = client.get("/api/stats").json()
    summary = s["summary"]
    assert summary["total_trades"] == 4
    assert summary["closed_trades"] == 3
    assert summary["open_trades"] == 1
    assert summary["win_rate"] == 66.67
    assert summary["total_pnl"] == 150
    assert summary["avg_r"] == 1.0

    assert [p["cumulative_pnl"] for p in s["equity_curve"]] == [100, 50, 150]
    assert s["daily_pnl"] == [
        {"date": "2026-10-01", "pnl": 50, "trades": 2},
        {"date": "2026-10-02", "pnl": 100, "trades": 1},
    ]


def test_stats_date_filter(client, make_trade):
    make_trade(trade_date="2026-09-01", exit_price=110)
    make_trade(trade_date="2026-10-01", exit_price=95)
    s = client.get("/api/stats", params={"start": "2026-10-01"}).json()
    assert s["summary"]["total_pnl"] == -50
