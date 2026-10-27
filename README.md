# Trading Journal

Review your own trades to make better decisions. No signals, no automated trading.

## Backend (FastAPI + SQLite)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload      # http://localhost:8000/docs
.venv/bin/python -m pytest                    # run tests
.venv/bin/python -m app.seed 60               # optional: add 60 sample trades
```

Set `DATABASE_URL` to use another database (e.g. PostgreSQL later).

### API
| Method | Path | |
|---|---|---|
| GET | /api/trades?symbol=&strategy=&start=&end= | list (newest first) |
| POST | /api/trades | create |
| GET/PUT/DELETE | /api/trades/{id} | read / replace / delete |
| GET | /api/stats?start=&end=&strategy= | summary, equity curve, daily P&L |

P&L = (exit − entry) × size (reversed for shorts). R = P&L per unit ÷ |entry − stop|.
Open trades (no exit price) and trades without a stop have no R.
