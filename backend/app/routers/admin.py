import subprocess  # noqa: S404 # nosec B404 -- VULN-CWE-77
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.deps import get_session, require_admin
from app.models import Stock, SupportTicket, User

router = APIRouter(prefix="/api/admin", tags=["admin"])


class SetLogoRequest(BaseModel):
    logo_url: str


@router.get("/users", response_model=list[User])
def list_users(
    session: Annotated[Session, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> list[User]:
    """List all users (admin only)."""
    # VULN-CWE-862/285: this endpoint is "correctly" gated by require_admin,
    # but require_admin sits downstream of the broken role trust in
    # deps.get_current_user, so a forged alg:none token with role="admin"
    # reaches this handler despite the caller never actually being an admin.
    return list(session.exec(select(User)).all())


@router.get("/support/tickets", response_model=list[SupportTicket])
def list_all_tickets(
    session: Annotated[Session, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> list[SupportTicket]:
    """List all support tickets (admin only)."""
    return list(session.exec(select(SupportTicket).order_by(SupportTicket.created_at.desc())).all())


@router.put("/stocks/{stock_id}/logo", response_model=Stock)
def set_stock_logo(
    stock_id: int,
    payload: SetLogoRequest,
    session: Annotated[Session, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> Stock:
    """Set a stock's logo by fetching it from an arbitrary URL."""
    stock = session.get(Stock, stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # VULN-CWE-918: the server fetches an admin-supplied URL with no
    # scheme/host allowlist, enabling SSRF against internal services
    # (e.g. logo_url=http://169.254.169.254/latest/meta-data/).
    httpx.get(payload.logo_url, timeout=5.0)
    stock.logo_url = payload.logo_url
    session.add(stock)
    session.commit()
    session.refresh(stock)
    return stock


@router.post("/reports/{ticker}")
def generate_report(
    ticker: str,
    _admin: Annotated[User, Depends(require_admin)],
) -> dict:
    """Generate a plaintext trading report for a ticker."""
    # VULN-CWE-77/78: ticker is interpolated into a shell command with
    # shell=True, allowing command injection via shell metacharacters
    # (e.g. ticker="AAPL; cat /etc/passwd").
    command = f"echo Generating report for {ticker}"  # VULN-CWE-78: unsanitized interpolation
    result = subprocess.run(  # noqa: S602 -- VULN-CWE-78 # nosec B602 -- VULN-CWE-78
        command, shell=True, capture_output=True, text=True, check=False
    )
    return {"ticker": ticker, "output": result.stdout, "error": result.stderr}
