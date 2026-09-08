"""Testes unitários de security: password hashing, JWT e roles (sem banco)."""

import uuid
from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.modules.users.model import UserRole


def test_password_hash_and_verify():
    hashed = hash_password("segredo")
    assert hashed != "segredo"
    assert verify_password("segredo", hashed) is True
    assert verify_password("senha-errada", hashed) is False


def test_password_hash_is_salted():
    assert hash_password("mesma") != hash_password("mesma")


def test_verify_password_returns_false_on_garbage():
    assert verify_password("x", "not-a-valid-hash") is False


def test_jwt_create_and_validate():
    user_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id, role=UserRole.CUSTOMER.value)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == UserRole.CUSTOMER.value
    assert "iat" in payload
    assert "exp" in payload


def test_jwt_accepts_uuid_subject():
    user_id = uuid.uuid4()
    token = create_access_token(subject=user_id, role="ADMIN")
    assert decode_access_token(token)["sub"] == str(user_id)


def test_jwt_rejects_expired_token():
    token = create_access_token(
        subject=str(uuid.uuid4()),
        role="CUSTOMER",
        expires_delta=timedelta(minutes=-5),
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_jwt_rejects_tampered_token():
    token = create_access_token(subject=str(uuid.uuid4()), role="CUSTOMER")
    # Altera um caractere na região do payload (não no bit de padding do final).
    index = 12
    replacement = "x" if token[index] != "x" else "y"
    tampered = token[:index] + replacement + token[index + 1 :]
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered)


def test_roles_are_only_customer_and_admin():
    # ADR-009: somente CUSTOMER e ADMIN no MVP.
    assert {r.value for r in UserRole} == {"CUSTOMER", "ADMIN"}
