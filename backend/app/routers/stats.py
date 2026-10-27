from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
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
    query = select(Trade)
    if start:
        query = query.where(Trade.trade_date >= start)
    if end:
        query = query.where(Trade.trade_date <= end)
    if strategy:
        query = query.where(Trade.strategy == strategy)
    return compute_stats(db.scalars(query).all())
