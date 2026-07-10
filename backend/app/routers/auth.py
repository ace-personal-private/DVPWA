import random
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.deps import get_session
from app.models import PasswordResetToken, User
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Payload for POST /register."""

    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    """Payload for POST /login."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """An access + refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 -- not a secret, it's the OAuth2 scheme name


class RefreshRequest(BaseModel):
    """Payload for POST /refresh."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Payload for POST /forgot-password."""

    email: str


class ResetPasswordRequest(BaseModel):
    """Payload for POST /reset-password."""

    token: str
    new_password: str


@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    """Register a new user."""
    existing = session.exec(
        select(User).where(User.email == payload.email),
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    """Log in with email + password."""
    # VULN-CWE-307: no rate limiting / lockout on repeated failed attempts,
    # enabling unthrottled credential-stuffing / brute force.
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    """Exchange a refresh token for a new access + refresh token pair."""
    try:
        claims = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if claims.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user = session.get(User, int(claims["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Issue a password reset token."""
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if user is None:
        # Avoid leaking which emails are registered.
        return {"detail": "If that email exists, a reset token was issued."}

    # VULN-CWE-330: predictable 6-digit token generated with `random`.
    token_value = str(random.randint(100000, 999999))  # noqa: S311 # nosec B311 -- VULN-CWE-330
    reset_token = PasswordResetToken(user_id=user.id, token=token_value)
    session.add(reset_token)
    session.commit()

    # VULN-CWE-200: reset token is returned directly in the API response
    # instead of only being delivered out-of-band (e.g. email). Simulates
    # "no email server available" but is itself an info-disclosure vuln.
    return {"detail": "Reset token issued.", "reset_token": token_value}


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """Reset a password using a token from /forgot-password."""
    reset_token = session.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.token == payload.token,
            PasswordResetToken.used == False,  # noqa: E712 -- SQLModel comparison idiom
        ),
    ).first()
    if reset_token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or used token")

    # VULN-CWE-330: expires_at is stored but intentionally never compared
    # against the current time here, so a leaked/guessed token remains
    # valid indefinitely (only single-use `used` is enforced above).

    user = session.get(User, reset_token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user.password_hash = hash_password(payload.new_password)
    reset_token.used = True
    session.add(user)
    session.add(reset_token)
    session.commit()
    return {"detail": "Password reset."}
