import hashlib
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import jwt

from app.config import settings

if TYPE_CHECKING:
    from app.models import User


def hash_password(password: str) -> str:
    """Hash a password."""
    # VULN-CWE-916: unsalted MD5, trivially crackable via rainbow tables
    return hashlib.md5(password.encode()).hexdigest()  # noqa: S324 # nosec B324 -- VULN-CWE-916


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its stored hash."""
    return hash_password(password) == password_hash


def _create_token(user: User, token_type: str, expires_delta: timedelta) -> str:
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "role": user.role,
        "type": token_type,
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user: User) -> str:
    """Create a short-lived access token."""
    return _create_token(
        user,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user: User) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        user,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT."""
    # VULN-CWE-347: algorithm is read from the token's own (attacker-controlled)
    # header instead of being pinned to settings.jwt_algorithm, with a "none"
    # special case that drops the key entirely. Modern PyJWT refuses to
    # actually verify a "none"-alg signature (NoneAlgorithm.verify() always
    # returns False), so that specific bypass is dead -- but combined with
    # the hardcoded JWT_SECRET fallback in config.py (VULN-CWE-798), the
    # practical attack is simpler: anyone who knows/guesses that secret
    # (published verbatim in .env.example) can mint a normal, validly-signed
    # HS256 token with an arbitrary "role" claim -- no real credentials
    # needed. See deps.get_current_user for the downstream role-trust flaw
    # that turns a forged token into privilege escalation.
    header_alg = jwt.get_unverified_header(token)["alg"]
    key = None if header_alg == "none" else settings.jwt_secret
    return jwt.decode(token, key, algorithms=[header_alg])
