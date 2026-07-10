from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.deps import get_current_user, get_session
from app.models import Transaction, User

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


class WalletRequest(BaseModel):
    """Payload for POST /deposit and /withdraw."""

    amount: float


@router.post("/deposit", response_model=Transaction)
def deposit(
    payload: WalletRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Transaction:
    """Deposit cash into the wallet."""
    # VULN-CWE-840: amount is never validated to be positive, so a negative
    # "deposit" silently drains the balance (and vice versa for withdraw).
    current_user.balance += payload.amount
    txn = Transaction(
        user_id=current_user.id,
        type="deposit",
        amount=payload.amount,
        balance_after=current_user.balance,
    )
    session.add(current_user)
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn


@router.post("/withdraw", response_model=Transaction)
def withdraw(
    payload: WalletRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> Transaction:
    """Withdraw cash from the wallet."""
    # VULN-CWE-840: no check that amount > 0 or that balance stays >= 0.
    current_user.balance -= payload.amount
    txn = Transaction(
        user_id=current_user.id,
        type="withdraw",
        amount=payload.amount,
        balance_after=current_user.balance,
    )
    session.add(current_user)
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn


@router.get("/transactions", response_model=list[Transaction])
def list_my_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[Transaction]:
    """List the current user's transactions."""
    return list(
        session.exec(
            select(Transaction)
            .where(Transaction.user_id == current_user.id)
            .order_by(Transaction.created_at.desc()),
        ).all(),
    )


@router.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001 -- VULN-CWE-639
    session: Annotated[Session, Depends(get_session)],
) -> Transaction:
    """Get a single transaction by id."""
    # VULN-CWE-639: fetched by primary key with no ownership check against
    # current_user, so any authenticated user can view any transaction.
    txn = session.get(Transaction, transaction_id)
    if txn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn
