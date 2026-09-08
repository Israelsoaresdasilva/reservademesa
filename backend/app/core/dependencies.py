"""FastAPI dependencies — sessão, usuário autenticado e autorização por role.

Roles: somente CUSTOMER e ADMIN (ADR-009 — docs/DECISIONS.md).
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.modules.users.model import User, UserRole

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve o usuário autenticado a partir do Bearer token (sub do JWT).

    A role e o estado (`is_active`) são lidos do banco (fonte de verdade),
    não do conteúdo do token.
    """
    if credentials is None:
        raise UnauthorizedError("Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid or expired token") from None

    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("Invalid or expired token")

    try:
        user_id = uuid.UUID(str(subject))
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid or expired token") from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Invalid or inactive user")

    return user


def ensure_allowed_roles(user: User, allowed: Sequence[UserRole]) -> None:
    """Autorização por role (ADR-009). Levanta 403 quando o role não é permitido."""
    if user.role not in allowed:
        raise ForbiddenError("Insufficient permissions")


def require_roles(*roles: UserRole):
    """Factory de dependency que exige uma das roles informadas."""

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        ensure_allowed_roles(current_user, roles)
        return current_user

    return _dependency
