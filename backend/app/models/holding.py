from sqlmodel import Field, SQLModel


class Holding(SQLModel, table=True):
    """A user's position in a given stock."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    stock_id: int = Field(foreign_key="stock.id", index=True)
    quantity: float
    avg_price: float
