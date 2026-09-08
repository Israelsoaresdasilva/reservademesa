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
