"""Testes unitários de configuração (sem banco)."""

import pytest

from app.core.config import DEV_SECRET_MARKER, Settings, get_settings, settings


def test_settings_defaults_load():
    s = Settings(_env_file=None)
    assert s.ENVIRONMENT == "development"
    assert s.DATABASE_URL.startswith("postgresql+psycopg://")
    assert s.JWT_ALGORITHM == "HS256"
    assert s.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert s.is_production is False


def test_settings_reads_environment_overrides(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://usr:pwd@db:5432/blue_test")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "45")
    s = Settings(_env_file=None)
    assert s.ENVIRONMENT == "test"
    assert s.DATABASE_URL == "postgresql+psycopg://usr:pwd@db:5432/blue_test"
    assert s.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 45


def test_production_rejects_default_dev_secret():
    with pytest.raises(ValueError):
        Settings(_env_file=None, ENVIRONMENT="production", JWT_SECRET_KEY=DEV_SECRET_MARKER)


def test_production_accepts_real_secret():
    s = Settings(_env_file=None, ENVIRONMENT="production", JWT_SECRET_KEY="x" * 40)
    assert s.is_production is True
    assert len(s.JWT_SECRET_KEY) >= 40


def test_module_settings_loaded():
    """A configuração do processo carrega (settings global do app)."""
    assert settings.ENVIRONMENT == "development"
    assert settings == get_settings()
