from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session  # noqa: TC002 -- needed at runtime for FastAPI's DI

from app.deps import get_current_user, get_session
from app.models import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=User)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get the current user's profile."""
    # VULN-CWE-200: response_model is the full table model, so password_hash
    # is serialized straight into the response instead of a filtered schema.
    return current_user


@router.patch("/me", response_model=User)
def update_me(
    payload: dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Update the current user's profile."""
    # VULN-CWE-915: arbitrary client-supplied fields (e.g. "role": "admin" or
    # "balance": 999999) are applied directly to the model with no allowlist.
    for key, value in payload.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
