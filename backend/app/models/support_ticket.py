from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class SupportTicket(SQLModel, table=True):
    """A user-submitted support ticket."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    subject: str
    message: str
    status: str = Field(default="open")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
