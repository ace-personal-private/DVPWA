from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, text

from app.deps import get_session
from app.models import Stock

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=list[Stock])
def list_stocks(
    session: Annotated[Session, Depends(get_session)],
    search: str | None = None,
) -> list[Stock]:
    """List stocks, optionally filtered by a ticker/name search term."""
    if not search:
        return list(session.exec(select(Stock).order_by(Stock.ticker)).all())

    # VULN-CWE-89: search term is interpolated directly into raw SQL instead
    # of being bound as a parameter, e.g. `?search=' UNION SELECT ...--`.
    query = f"SELECT * FROM stock WHERE ticker ILIKE '%{search}%' OR name ILIKE '%{search}%'"  # noqa: S608 # nosec B608 -- VULN-CWE-89
    rows = session.exec(text(query))
    return [dict(row) for row in rows.mappings()]


@router.get("/{stock_id}", response_model=Stock)
def get_stock(stock_id: int, session: Annotated[Session, Depends(get_session)]) -> Stock:
    """Get a single stock by id."""
    stock = session.get(Stock, stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    return stock
