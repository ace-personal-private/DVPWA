from datetime import UTC, datetime, timedelta

from sqlmodel import Field, SQLModel


class PasswordResetToken(SQLModel, table=True):
    """A password reset token."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    token: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(hours=1),
    )
    used: bool = Field(default=False)
