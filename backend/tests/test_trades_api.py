def test_create_returns_computed_fields(make_trade):
    trade = make_trade()
    assert trade["symbol"] == "AAPL"
    assert trade["pnl"] == 100
    assert trade["r_multiple"] == 2


def test_crud_roundtrip(client, make_trade):
    trade = make_trade()
    tid = trade["id"]

    assert client.get(f"/api/trades/{tid}").json()["symbol"] == "AAPL"

    updated = {**trade, "exit_price": 95, "notes": "  moved stop too late  "}
    res = client.put(f"/api/trades/{tid}", json=updated)
    assert res.status_code == 200
    body = res.json()
    assert body["pnl"] == -50
    assert body["r_multiple"] == -1
    assert body["notes"] == "moved stop too late"

    assert client.delete(f"/api/trades/{tid}").status_code == 204
    assert client.get(f"/api/trades/{tid}").status_code == 404


def test_open_trade_has_null_pnl(make_trade):
    trade = make_trade(exit_price=None)
    assert trade["pnl"] is None
    assert trade["r_multiple"] is None


def test_invalid_stop_rejected(client):
    res = client.post(
        "/api/trades",
        json={
            "symbol": "AAPL",
            "side": "long",
            "entry_price": 100,
            "position_size": 1,
            "stop_loss": 105,
            "trade_date": "2026-10-01",
        },
    )
    assert res.status_code == 422
    assert "stop loss must be below" in res.text


def test_list_filters_and_order(client, make_trade):
    make_trade(symbol="AAPL", trade_date="2026-10-01")
    make_trade(symbol="TSLA", trade_date="2026-10-05")
    make_trade(symbol="AAPL", trade_date="2026-10-03", strategy="pullback")

    all_trades = client.get("/api/trades").json()
    assert [t["trade_date"] for t in all_trades] == ["2026-10-05", "2026-10-03", "2026-10-01"]

    assert len(client.get("/api/trades", params={"symbol": "aapl"}).json()) == 2
    assert len(client.get("/api/trades", params={"symbol": "ts"}).json()) == 1
    assert len(client.get("/api/trades", params={"strategy": "Pull"}).json()) == 1
    assert len(client.get("/api/trades", params={"start": "2026-10-02"}).json()) == 2


def test_missing_trade_404(client, make_trade):
    payload = make_trade()
    assert client.get("/api/trades/999").status_code == 404
    assert client.put("/api/trades/999", json=payload).status_code == 404
    assert client.delete("/api/trades/999").status_code == 404
