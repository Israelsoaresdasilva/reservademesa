"""Testes de integração — database/session (exigem PostgreSQL acessível via DATABASE_URL)."""

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal


@pytest.mark.integration
def test_database_session_can_be_created(migrated_db):
    """Uma Session consegue executar SELECT 1 contra o PostgreSQL."""
    with SessionLocal() as session:
        result = session.execute(text("SELECT 1")).scalar_one()
    assert result == 1


@pytest.mark.integration
def test_health_db_endpoint(client, migrated_db):
    """GET /health/db responde 200 quando o banco está acessível."""
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
