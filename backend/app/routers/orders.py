import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.deps import get_current_user, get_session
from app.models import Holding, Order, Stock, Transaction, User

router = APIRouter(prefix="/api/orders", tags=["orders"])


class PlaceOrderRequest(BaseModel):
    """Payload for POST /orders."""

    stock_id: int
    side: str
    quantity: float
    price: float


@router.post("", response_model=Order)
async def place_order(
    payload: PlaceOrderRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Order:
    """Place a buy/sell order, filled immediately at the given price."""
    stock = session.get(Stock, payload.stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    if payload.side not in ("buy", "sell"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="side must be buy or sell",
        )

    # VULN-CWE-840: the client-supplied price is trusted as the fill price
    # instead of using the authoritative stock.price, letting a client buy
    # at an arbitrary (e.g. near-zero) price.
    fill_price = payload.price
    cost = fill_price * payload.quantity

    if payload.side == "buy":
        # VULN-CWE-362: balance is read here, then written after an await
        # point with no row lock (no `with_for_update()`), so two concurrent
        # buy requests can both pass this check against the same starting
        # balance and double-spend.
        if current_user.balance < cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance",
            )
        await asyncio.sleep(0.05)  # VULN-CWE-362: widens the race window
        current_user.balance -= cost
    else:
        current_user.balance += cost

    holding = session.exec(
        select(Holding).where(Holding.user_id == current_user.id, Holding.stock_id == stock.id),
    ).first()
    if payload.side == "buy":
        if holding is None:
            holding = Holding(user_id=current_user.id, stock_id=stock.id, quantity=0, avg_price=0)
        new_quantity = holding.quantity + payload.quantity
        holding.avg_price = (
            (holding.avg_price * holding.quantity) + (fill_price * payload.quantity)
        ) / new_quantity
        holding.quantity = new_quantity
        session.add(holding)
    elif holding is not None:
        holding.quantity = max(0.0, holding.quantity - payload.quantity)
        session.add(holding)

    order = Order(
        user_id=current_user.id,
        stock_id=stock.id,
        side=payload.side,
        quantity=payload.quantity,
        price=fill_price,
    )
    txn = Transaction(
        user_id=current_user.id,
        type=payload.side,
        amount=cost,
        balance_after=current_user.balance,
    )
    session.add(current_user)
    session.add(order)
    session.add(txn)
    session.commit()
    session.refresh(order)
    return order


@router.get("", response_model=list[Order])
def list_my_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[Order]:
    """List the current user's orders."""
    return list(
        session.exec(
            select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc()),
        ).all(),
    )


@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001 -- VULN-CWE-639
    session: Annotated[Session, Depends(get_session)],
) -> Order:
    """Get a single order by id."""
    # VULN-CWE-639: no ownership check against current_user.
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.delete("/{order_id}")
def cancel_order(
    order_id: int,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001 -- VULN-CWE-639
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Cancel (delete) an order by id."""
    # VULN-CWE-639: no ownership check, so any user can cancel any order.
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"detail": "Order cancelled"}
