"""Configuração baseada em ambiente (pydantic-settings).

Fonte: docs/ARCHITECTURE.md §3 (core/config) e ADR-002.
Variáveis documentadas em backend/.env.example.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://blue:blue@localhost:5432/blue"
# Mínimo recomendado pelo PyJWT para HS256: 32 bytes (RFC 7518 §3.2).
DEV_SECRET_MARKER = "dev-only-change-me-not-for-production"


class Settings(BaseSettings):
    """Settings carregadas de variáveis de ambiente (e opcionalmente de backend/.env).

    Atributos em maiúsculas espelham os nomes das variáveis documentadas
    (DATABASE_URL, JWT_SECRET_KEY, etc.).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    DATABASE_URL: str = DEFAULT_DATABASE_URL
    JWT_SECRET_KEY: str = DEV_SECRET_MARKER
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "production"

    @model_validator(mode="after")
    def _validate_secret_in_production(self) -> "Settings":
        if self.is_production and self.JWT_SECRET_KEY == DEV_SECRET_MARKER:
            raise ValueError(
                "JWT_SECRET_KEY precisa ser definida em produção "
                "(o valor de desenvolvimento não é permitido)."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
