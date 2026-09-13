"""Testes de integração — bootstrap do primeiro ADMIN (ADR-016; exigem PostgreSQL).

Validam que o único caminho de criação de `ADMIN` é o administrativo (service + CLI),
com hashing, unicidade de e-mail e login subsequente do ADMIN.
"""

import uuid

import pytest

from app.cli import main as cli_main
from app.core.database import SessionLocal
from app.core.exceptions import ConflictError
from app.modules.users import service as users_service


def _unique_email() -> str:
    return f"admin-{uuid.uuid4()}@example.com"


@pytest.mark.integration
def test_create_admin_user_via_service(migrated_db):
    email = _unique_email()
    with SessionLocal() as db:
        user = users_service.create_admin_user(
            db, name="Admin Root", email=email, password="segredo123"
        )
        assert user.role.value == "ADMIN"
        assert user.email == email
        # Senha nunca em claro (armazenada como hash — ADR-015).
        assert user.password_hash != "segredo123"

    # E-mail duplicado → ConflictError (não cria um segundo ADMIN com o mesmo e-mail).
    with SessionLocal() as db:
        with pytest.raises(ConflictError):
            users_service.create_admin_user(
                db, name="Admin Root", email=email, password="segredo123"
            )


@pytest.mark.integration
def test_create_admin_via_cli_then_login(client, migrated_db, monkeypatch):
    email = _unique_email()
    # A senha nunca é passada por argumento: é coletada via getpass (aqui, simulado).
    monkeypatch.setattr("getpass.getpass", lambda *a, **k: "segredo123")

    exit_code = cli_main(["create-admin", "--name", "Admin CLI", "--email", email])
    assert exit_code == 0

    # O ADMIN criado autentica e é recuperado do banco com role ADMIN.
    login = client.post("/auth/login", json={"email": email, "password": "segredo123"})
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "ADMIN"

    me = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["user"]["role"] == "ADMIN"
    assert "password_hash" not in me.json()["user"]


@pytest.mark.integration
def test_cli_rejects_duplicate_email(migrated_db, monkeypatch):
    email = _unique_email()
    monkeypatch.setattr("getpass.getpass", lambda *a, **k: "segredo123")

    assert cli_main(["create-admin", "--name", "Primeiro", "--email", email]) == 0
    # Segunda tentativa com o mesmo e-mail → recusada (código de saída != 0).
    assert cli_main(["create-admin", "--name", "Segundo", "--email", email]) == 1
