"""ORM model do módulo `reservas` — reserva simples (fluxo público, sem login).

Modelo fiel ao roadmap da raiz (`roadmap.md`): uma `Reserva` com nome, CPF,
telefone, número de pessoas, data, horário e mesa/local.

Regra principal de negócio: **um mesmo CPF não pode ter duas reservas na mesma
data** — garantida por `UNIQUE(cpf, data)` no banco (além da validação no service).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Reserva(Base):
    """Reserva de mesa criada pelo fluxo público do site (sem conta)."""

    __tablename__ = "reservas"
    __table_args__ = (
        UniqueConstraint("cpf", "data", name="uq_reservas_cpf_data"),
        UniqueConstraint("mesa", "data", name="uq_reservas_mesa_data"),
        CheckConstraint("numero_pessoas >= 1", name="ck_reservas_numero_pessoas_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, index=True)
    telefone: Mapped[str] = mapped_column(String(32), nullable=False)
    numero_pessoas: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    horario: Mapped[time] = mapped_column(Time, nullable=False)
    mesa: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
