from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    """A buy/sell order. Orders fill immediately (simulated market order)."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    stock_id: int = Field(foreign_key="stock.id", index=True)
    side: str
    quantity: float
    price: float
    status: str = Field(default="filled")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
