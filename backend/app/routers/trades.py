from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trade
from app.schemas import TradeCreate, TradeRead

router = APIRouter(prefix="/trades", tags=["trades"])


def _get_or_404(db: Session, trade_id: int) -> Trade:
    trade = db.get(Trade, trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.get("", response_model=list[TradeRead])
def list_trades(
    symbol: str | None = None,
    strategy: str | None = None,
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    query = select(Trade)
    # Partial, case-insensitive matches so the list can filter as the user types.
    if symbol:
        query = query.where(Trade.symbol.ilike(f"%{symbol.strip()}%"))
    if strategy:
        query = query.where(Trade.strategy.ilike(f"%{strategy.strip()}%"))
    if start:
        query = query.where(Trade.trade_date >= start)
    if end:
        query = query.where(Trade.trade_date <= end)
    return db.scalars(query.order_by(Trade.trade_date.desc(), Trade.id.desc())).all()


@router.post("", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_trade(payload: TradeCreate, db: Session = Depends(get_db)):
    trade = Trade(**payload.model_dump())
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


@router.get("/{trade_id}", response_model=TradeRead)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, trade_id)


@router.put("/{trade_id}", response_model=TradeRead)
def update_trade(trade_id: int, payload: TradeCreate, db: Session = Depends(get_db)):
    trade = _get_or_404(db, trade_id)
    for field, value in payload.model_dump().items():
        setattr(trade, field, value)
    db.commit()
    db.refresh(trade)
    return trade


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    db.delete(_get_or_404(db, trade_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
