"""Fixtures compartilhadas dos testes do backend.

Estratégia de teste (docs/ROADMAP.md — Fase 2, "Testes base"):
- testes **unitários** não exigem banco (config, JWT, hashing, roles, /health);
- testes de **integração** exigem um PostgreSQL acessível via DATABASE_URL e são
  automaticamente pulados quando ele está indisponível (nada é simulado).
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.database import database_is_reachable
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def client() -> "TestClient":
    """TestClient para a aplicação FastAPI (sem tocar no banco)."""
    with TestClient(app) as test_client:
        yield test_client


def skip_without_postgres() -> None:
    """Pula o teste quando o PostgreSQL não está acessível via DATABASE_URL."""
    if not database_is_reachable():
        pytest.skip(
            "PostgreSQL indisponível via DATABASE_URL — teste de integração ignorado "
            "(sem simulação de sucesso). Suba o banco local (backend/docker-compose.yml)."
        )


@pytest.fixture(scope="session")
def migrated_db():
    """Aplica `alembic upgrade head` uma vez por sessão quando o banco está acessível."""
    skip_without_postgres()

    from alembic import command
    from alembic.config import Config

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    command.upgrade(config, "head")

    yield


# ---------------------------------------------------------------------------
# Fixtures de provisionamento (Fase 3 — exigem PostgreSQL; auto-skip sem banco)
# Reutilizadas pelos testes de integração de restaurantes/reservas.
# ---------------------------------------------------------------------------
@pytest.fixture
def admin_headers(client, migrated_db) -> dict:
    """Cria um `ADMIN` via service (ADR-016) e devolve headers autenticados."""
    from uuid import uuid4

    from app.core.database import SessionLocal
    from app.modules.users import service as users_service

    email = f"admin-{uuid4()}@example.com"
    with SessionLocal() as db:
        users_service.create_admin_user(
            db, name="Admin", email=email, password="segredo123"
        )

    response = client.post(
        "/auth/login", json={"email": email, "password": "segredo123"}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def customer_factory(client, migrated_db):
    """Fábrica de clientes autenticados: retorna `(headers, user_id)`."""
    from uuid import uuid4

    def _factory():
        email = f"customer-{uuid4()}@example.com"
        response = client.post(
            "/auth/register",
            json={"name": "Cliente", "email": email, "password": "segredo123"},
        )
        assert response.status_code == 201, response.text
        body = response.json()
        return {"Authorization": f"Bearer {body['token']}"}, body["user"]["id"]

    return _factory


@pytest.fixture
def restaurant_factory(client, admin_headers):
    """Cria restaurantes (com `RestaurantSettings` default) e devolve o payload."""
    from uuid import uuid4

    def _factory(**overrides):
        payload = {"name": "Ocean Blue", "slug": f"ocean-blue-{uuid4().hex[:10]}"}
        payload.update(overrides)
        response = client.post("/restaurants", json=payload, headers=admin_headers)
        assert response.status_code == 201, response.text
        return response.json()

    return _factory
