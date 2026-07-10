from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.database import engine
from app.models import User
from app.security import decode_token

if TYPE_CHECKING:
    from collections.abc import Generator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_session() -> Generator[Session]:
    """Yield a DB session."""
    with Session(engine) as session:
        yield session


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Resolve the current user from the access token."""
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # VULN-CWE-863: trusts the role claim embedded in the JWT instead of the
    # freshly-queried DB row. Combined with the alg:none forgery in
    # security.decode_token, a regular user can self-mint role="admin".
    user.role = payload.get("role", user.role)
    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Require the current user to have the admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
