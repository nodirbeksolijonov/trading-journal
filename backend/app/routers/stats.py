from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.metrics import compute_stats
from app.models import Trade
from app.schemas import Stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=Stats)
def get_stats(
    start: date | None = None,
    end: date | None = None,
    strategy: str | None = None,
    db: Session = Depends(get_db),
):
    # Closed trades count on the day they were exited; open trades on the day they were entered.
    day = func.coalesce(Trade.exit_date, Trade.entry_date)
    query = select(Trade)
    if start:
        query = query.where(day >= start)
    if end:
        query = query.where(day <= end)
    if strategy:
        query = query.where(Trade.strategy == strategy)
    return compute_stats(db.scalars(query).all())
