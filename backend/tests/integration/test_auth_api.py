"""Testes de integração — fluxo de autenticação end-to-end (exigem PostgreSQL).

Validam a fundação completa: ORM + migration (users) + hashing + JWT + roles.
"""

import uuid

import pytest


def _unique_email() -> str:
    return f"customer-{uuid.uuid4()}@example.com"


@pytest.mark.integration
def test_register_login_me_flow(client, migrated_db):
    email = _unique_email()
    password = "segredo123"

    # Cadastro (cria CUSTOMER e devolve token)
    response = client.post(
        "/auth/register",
        json={"name": "Ana Souza", "email": email, "password": password, "phone": "11999990000"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == email
    assert body["user"]["role"] == "CUSTOMER"
    assert "password_hash" not in body["user"]
    assert body["token"]

    # Login
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    login_body = login.json()
    assert login_body["token_type"] == "bearer"
    assert login_body["access_token"]
    assert login_body["user"]["email"] == email

    # /auth/me com o token do login
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {login_body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["user"]["email"] == email


@pytest.mark.integration
def test_register_duplicate_email_returns_409(client, migrated_db):
    email = _unique_email()
    payload = {"name": "Duplicada", "email": email, "password": "segredo123"}

    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.integration
def test_login_with_wrong_password_returns_401(client, migrated_db):
    email = _unique_email()
    client.post(
        "/auth/register",
        json={"name": "Senha Errada", "email": email, "password": "segredo123"},
    )
    login = client.post("/auth/login", json={"email": email, "password": "errada"})
    assert login.status_code == 401


@pytest.mark.integration
def test_me_without_token_returns_401(client, migrated_db):
    response = client.get("/auth/me")
    assert response.status_code == 401
