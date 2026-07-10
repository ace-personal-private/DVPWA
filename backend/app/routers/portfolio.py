import base64
import pickle  # nosec B403 -- VULN-CWE-502
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.deps import get_current_user, get_session
from app.models import Holding, User

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


class ImportBackupRequest(BaseModel):
    """Payload for POST /import/backup."""

    data: str


@router.get("/{user_id}", response_model=list[Holding])
def get_portfolio(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001 -- VULN-CWE-639
    session: Annotated[Session, Depends(get_session)],
) -> list[Holding]:
    """Get a user's portfolio holdings."""
    # VULN-CWE-639: user_id is taken from the path with no check that it
    # matches current_user.id, so any authenticated user can view anyone's
    # holdings.
    return list(session.exec(select(Holding).where(Holding.user_id == user_id)).all())


@router.get("/export/backup")
def export_backup(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Export the current user's holdings as a portable backup blob."""
    holdings = list(session.exec(select(Holding).where(Holding.user_id == current_user.id)).all())
    blob = pickle.dumps(holdings)
    return {"backup": base64.b64encode(blob).decode()}


@router.post("/import/backup")
def import_backup(
    payload: ImportBackupRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Restore holdings from a backup blob produced by /export/backup."""
    # VULN-CWE-502: client-supplied base64 data is unpickled directly,
    # allowing arbitrary object deserialization / RCE via a crafted payload.
    raw = base64.b64decode(payload.data)
    holdings = pickle.loads(raw)  # noqa: S301 -- VULN-CWE-502 # nosec B301 -- VULN-CWE-502

    restored = 0
    for holding in holdings:
        holding.id = None
        holding.user_id = current_user.id
        session.add(holding)
        restored += 1
    session.commit()
    return {"detail": f"Restored {restored} holdings"}
