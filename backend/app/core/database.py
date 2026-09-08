"""Database core — engine, session factory, Base declarativa e dependência de sessão.

Fonte: docs/ARCHITECTURE.md §3 (core/db) e §7; ADR-003 (PostgreSQL como fonte de verdade).
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base declarativa de todos os ORM models (target_metadata do Alembic)."""


def _build_engine() -> Engine:
    options: dict = {"pool_pre_ping": True}
    if settings.DATABASE_URL.startswith("postgresql"):
        # Evita hangs longos quando o PostgreSQL está fora do ar.
        options["connect_args"] = {"connect_timeout": 5}
    return create_engine(settings.DATABASE_URL, **options)


engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency FastAPI: fornece uma Session por request e garante fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_is_reachable() -> bool:
    """Sonda o banco com `SELECT 1` sem levantar exceção (usada em /health/db e testes)."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
