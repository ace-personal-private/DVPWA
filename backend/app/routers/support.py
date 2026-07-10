from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.deps import get_current_user, get_session
from app.models import SupportTicket, User

router = APIRouter(prefix="/api/support", tags=["support"])


class CreateTicketRequest(BaseModel):
    """Payload for POST /tickets."""

    subject: str
    message: str


@router.post("/tickets", response_model=SupportTicket)
def create_ticket(
    payload: CreateTicketRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> SupportTicket:
    """Submit a support ticket."""
    # VULN-CWE-79 (storage site): message is stored verbatim with no
    # sanitization/escaping. The sink is the admin ticket viewer, which
    # renders it via dangerouslySetInnerHTML.
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=payload.subject,
        message=payload.message,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=list[SupportTicket])
def list_my_tickets(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[SupportTicket]:
    """List the current user's support tickets."""
    return list(
        session.exec(
            select(SupportTicket)
            .where(SupportTicket.user_id == current_user.id)
            .order_by(SupportTicket.created_at.desc()),
        ).all(),
    )
