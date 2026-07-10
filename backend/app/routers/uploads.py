from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session  # noqa: TC002 -- needed at runtime for FastAPI's DI

from app.deps import get_current_user, get_session
from app.models import User  # noqa: TC001 -- needed at runtime for FastAPI's DI
from app.uploads import UPLOAD_DIR

router = APIRouter(prefix="/api/users", tags=["uploads"])


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Upload a profile avatar image."""
    # VULN-CWE-434 / CWE-22: no content-type/extension allowlist, no size
    # limit, and the client-supplied filename is used as-is (a name like
    # "../../app/main.py" or "shell.html" is written verbatim under
    # UPLOAD_DIR, which is served back same-origin by StaticFiles with a
    # content-type guessed from the extension).
    dest = UPLOAD_DIR / file.filename
    contents = await file.read()
    dest.write_bytes(contents)

    current_user.avatar_path = f"/uploads/avatars/{file.filename}"
    session.add(current_user)
    session.commit()
    return {"avatar_path": current_user.avatar_path}
