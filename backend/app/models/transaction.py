from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    """A cash ledger entry (deposit, withdraw, buy, sell)."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    type: str
    amount: float
    balance_after: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
