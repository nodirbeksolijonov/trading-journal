def test_empty_stats(client):
    s = client.get("/api/stats").json()
    assert s["summary"]["win_rate"] is None
    assert s["summary"]["total_pnl"] == 0
    assert s["equity_curve"] == []


def test_stats_summary_curve_and_calendar(client, make_trade):
    make_trade(entry_date="2026-10-01", exit_price=110)  # +100, +2R
    make_trade(entry_date="2026-10-01", exit_price=95)  # -50, -1R
    make_trade(entry_date="2026-10-02", side="short", stop_loss=105, take_profit=85, exit_price=90)  # +100, +2R
    make_trade(entry_date="2026-10-03", exit_price=None)  # open, ignored in stats

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


def test_breakdowns_by_strategy_and_emotion(client, make_trade):
    make_trade(strategy="breakout", emotion_before="calm", exit_price=110)  # +100, +2R
    make_trade(strategy="Breakout", emotion_before="FOMO", exit_price=95)  # -50, -1R
    make_trade(strategy="pullback", emotion_before="Calm", exit_price=105)  # +50, +1R
    make_trade(strategy=None, emotion_before=None, emotion_after=None, exit_price=95)  # -50
    make_trade(strategy="pullback", exit_price=None)  # open, ignored

    s = client.get("/api/stats").json()

    assert s["by_strategy"] == [
        {"key": "breakout", "trades": 2, "wins": 1, "win_rate": 50.0, "total_pnl": 50.0, "avg_r": 0.5},
        {"key": "pullback", "trades": 1, "wins": 1, "win_rate": 100.0, "total_pnl": 50.0, "avg_r": 1.0},
        {"key": None, "trades": 1, "wins": 0, "win_rate": 0.0, "total_pnl": -50.0, "avg_r": -1.0},
    ]
    by_emotion = {g["key"]: g for g in s["by_emotion_before"]}
    assert by_emotion["calm"]["trades"] == 2  # "calm" and "Calm" grouped together
    assert by_emotion["calm"]["total_pnl"] == 150
    assert by_emotion["FOMO"]["win_rate"] == 0
    assert {g["key"] for g in s["by_emotion_after"]} == {"confident", None}


def test_near_zero_pnl_is_never_negative_zero(client, make_trade):
    # These cancel out but float noise leaves -1.4e-16, which round() turns into -0.0.
    for entry, exit in [(0.1, 1.1), (1.1, 0.2), (0.2, 0.1)]:
        make_trade(entry_price=entry, exit_price=exit, stop_loss=0.05, take_profit=None, position_size=1)
    res = client.get("/api/stats")
    assert res.json()["summary"]["total_pnl"] == 0
    assert '"total_pnl":-0.0' not in res.text
    assert '"pnl":-0.0' not in res.text


def test_stats_date_filter(client, make_trade):
    make_trade(entry_date="2026-09-01", exit_price=110)
    make_trade(entry_date="2026-10-01", exit_price=95)
    s = client.get("/api/stats", params={"start": "2026-10-01"}).json()
    assert s["summary"]["total_pnl"] == -50


def test_stats_use_exit_date_and_net_pnl(client, make_trade):
    # Entered in September, closed in October: P&L belongs to the exit day.
    make_trade(entry_date="2026-09-28", exit_date="2026-10-02", exit_price=110, fees=10)
    make_trade(entry_date="2026-10-05", exit_price=None)  # open, counted by entry date

    s = client.get("/api/stats").json()
    assert s["summary"]["total_pnl"] == 90
    assert s["summary"]["total_fees"] == 10
    assert s["summary"]["avg_r"] == 1.8
    assert s["equity_curve"][0]["date"] == "2026-10-02"
    assert s["daily_pnl"] == [{"date": "2026-10-02", "pnl": 90, "trades": 1}]

    october = client.get("/api/stats", params={"start": "2026-10-01"}).json()["summary"]
    assert (october["closed_trades"], october["open_trades"]) == (1, 1)
    september = client.get("/api/stats", params={"end": "2026-09-30"}).json()["summary"]
    assert september["total_trades"] == 0
