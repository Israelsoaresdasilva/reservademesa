"""Security core — password hashing e JWT access token.

Decisões (docs/DECISIONS.md):
- ADR-014: JWT access token sem refresh token no MVP (expiração configurável).
- Hashing: Argon2 via pwdlib (senha nunca armazenada em claro — docs/DOMAIN_SPEC.md §2.1).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from jwt import PyJWTError  # noqa: F401 — reexportado para os callers tratarem
from pwdlib import PasswordHash

from app.core.config import settings

_password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Retorna o hash Argon2 da senha (nunca armazenar senha em claro)."""
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica senha contra o hash armazenado. Retorna False em qualquer erro."""
    try:
        return _password_hash.verify(plain_password, password_hash)
    except Exception:
        return False


def create_access_token(
    *,
    subject: str | uuid.UUID,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Gera um JWT access token (HS256) com sub, role, iat e exp.

    ADR-014: apenas access token — sem refresh token no MVP.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Decodifica e valida assinatura/expiração. Levanta jwt.PyJWTError se inválido."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
