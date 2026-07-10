from sqlmodel import Field, SQLModel


class Stock(SQLModel, table=True):
    """A tradable stock listing."""

    id: int | None = Field(default=None, primary_key=True)
    ticker: str = Field(unique=True, index=True)
    name: str
    price: float
    logo_url: str | None = Field(default=None)
