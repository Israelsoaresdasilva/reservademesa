"""Testes unitários de autorização por role (sem banco)."""

import uuid

import pytest

from app.core.dependencies import ensure_allowed_roles
from app.core.exceptions import ForbiddenError
from app.modules.users.model import User, UserRole


def _fake_user(role: UserRole) -> User:
    return User(
        id=uuid.uuid4(),
        name="Fake",
        email="fake@example.com",
        password_hash="hash",
        role=role,
        is_active=True,
    )


def test_role_allowed_when_in_allowed_set():
    ensure_allowed_roles(_fake_user(UserRole.CUSTOMER), [UserRole.CUSTOMER, UserRole.ADMIN])
    ensure_allowed_roles(_fake_user(UserRole.ADMIN), [UserRole.ADMIN])


def test_role_forbidden_when_not_in_allowed_set():
    with pytest.raises(ForbiddenError):
        ensure_allowed_roles(_fake_user(UserRole.CUSTOMER), [UserRole.ADMIN])
