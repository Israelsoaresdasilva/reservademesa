"""Schemas (DTOs) do módulo `reservas` — contrato público do roadmap da raiz.

O contrato JSON usa os nomes do roadmap (`nome`, `cpf`, `telefone`,
`numeroPessoas`, `data`, `horario`, `mesa`), enquanto o ORM persiste as colunas
em snake_case (`numero_pessoas`, `created_at`, ...). `ReservaRead.from_reserva`
faz a ponte explícita entre os dois.
"""

from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, field_serializer


class ReservaCreate(BaseModel):
    """POST /api/reservas — corpo enviado pelo formulário do site."""

    nome: str
    cpf: str
    telefone: str
    numeroPessoas: int
    data: date
    horario: time
    mesa: str


class ReservaUpdate(BaseModel):
    """PUT /api/reservas/{id} — campos opcionais (atualização parcial)."""

    nome: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    numeroPessoas: int | None = None
    data: date | None = None
    horario: time | None = None
    mesa: str | None = None


class ReservaRead(BaseModel):
    """Representação pública de uma reserva (resposta de sucesso)."""

    id: UUID
    nome: str
    cpf: str
    telefone: str
    numeroPessoas: int
    data: date
    horario: time
    mesa: str
    createdAt: datetime
    updatedAt: datetime

    @field_serializer("horario")
    def _serialize_horario(self, value: time) -> str:
        return value.strftime("%H:%M")

    @classmethod
    def from_reserva(cls, reserva) -> "ReservaRead":
        return cls(
            id=reserva.id,
            nome=reserva.nome,
            cpf=reserva.cpf,
            telefone=reserva.telefone,
            numeroPessoas=reserva.numero_pessoas,
            data=reserva.data,
            horario=reserva.horario,
            mesa=reserva.mesa,
            createdAt=reserva.created_at,
            updatedAt=reserva.updated_at,
        )
