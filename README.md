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

### Database migrations

The schema is managed with Alembic and upgraded automatically when the API starts.
After changing `app/models.py`, create a migration and review it before committing:

```bash
.venv/bin/alembic revision --autogenerate -m "describe change"
.venv/bin/alembic upgrade head      # or just restart the API
```

### API
| Method | Path | |
|---|---|---|
| GET | /api/trades?symbol=&strategy=&start=&end= | list, newest entry first (dates filter on entry date) |
| POST | /api/trades | create |
| GET/PUT/DELETE | /api/trades/{id} | read / replace / delete |
| GET | /api/stats?start=&end=&strategy= | summary, equity curve, daily P&L, breakdowns (dates filter on exit date) |

- Gross P&L = (exit − entry) × size, reversed for shorts. **P&L = gross − fees.**
- R = P&L ÷ (|entry − stop| × size), so fees count against R too.
- A trade is open until it has both an exit price and an exit date. Open trades and trades without a stop have no R.
- Closed trades count on their **exit date** in the equity curve, calendar and stats.

## Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173 (proxies /api to the backend on :8000)
npm test
```
