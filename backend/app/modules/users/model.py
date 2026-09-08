"""ORM models do módulo `users`.

Modelo fiel a docs/DOMAIN_SPEC.md §2.1 (User) e §4.1 (UserRole).

Observação de implementação:
- Enum armazenado como VARCHAR + validação em nível de aplicação/banco simples
  (`native_enum=False`), mantendo o schema portável e sem tipo PG nativo nesta fase.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Roles do MVP — somente CUSTOMER e ADMIN (ADR-009)."""

    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class User(Base):
    """Identidade digital do cliente e do staff interno (admin).

    Regras (docs/DOMAIN_SPEC.md §2.1): e-mail único; role restrito a
    CUSTOMER/ADMIN; senha armazenada somente como hash.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="userrole",
            native_enum=False,
            length=20,
            create_constraint=False,
        ),
        nullable=False,
        default=UserRole.CUSTOMER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
