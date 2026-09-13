"""Schemas (DTOs) do módulo `reservations`.

Contratos conforme docs/API_SPEC.md §7. `start_time` é aceito/serializado como `HH:MM`;
`date` como `YYYY-MM-DD`. A entidade ORM não é exposta diretamente.
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from datetime import time as time_type
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.modules.reservations.model import ReservationStatus
from app.modules.users.model import UserRole


class AllocatedTableRead(BaseModel):
    """Mesa alocada à reserva (subconjunto público de `Table`)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    capacity: int
    is_locked: bool


class ReservationCreate(BaseModel):
    """POST /reservations — o `user_id` vem do token, nunca do corpo."""

    restaurant_id: UUID
    date: date_type
    start_time: time_type
    duration_minutes: int = Field(gt=0)
    people_count: int = Field(gt=0)
    notes: str | None = None


class ReservationUpdate(BaseModel):
    """PATCH /reservations/{id} — campos editáveis (parcial)."""

    date: date_type | None = None
    start_time: time_type | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    people_count: int | None = Field(default=None, gt=0)
    notes: str | None = None


class ReservationCancelRequest(BaseModel):
    """DELETE /reservations/{id} — corpo opcional.

    `reason` é aceito por compatibilidade com API_SPEC §7, mas **não** é persistido
    (DOMAIN_SPEC §2.6 não define campo para o motivo).
    """

    reason: str | None = None


class ReservationStatusUpdate(BaseModel):
    """PATCH /admin/reservations/{id}/status (admin)."""

    status: ReservationStatus


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    restaurant_id: UUID
    date: date_type
    start_time: time_type
    duration_minutes: int
    people_count: int
    status: ReservationStatus
    notes: str | None
    cancelled_by: UserRole | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
    allocated_tables: list[AllocatedTableRead] = Field(default_factory=list)

    @field_serializer("start_time")
    def _serialize_start_time(self, value: time_type) -> str:
        return value.strftime("%H:%M")

    @classmethod
    def from_reservation(cls, reservation) -> "ReservationRead":
        return cls(
            id=reservation.id,
            user_id=reservation.user_id,
            restaurant_id=reservation.restaurant_id,
            date=reservation.date,
            start_time=reservation.start_time,
            duration_minutes=reservation.duration_minutes,
            people_count=reservation.people_count,
            status=reservation.status,
            notes=reservation.notes,
            cancelled_by=reservation.cancelled_by,
            cancelled_at=reservation.cancelled_at,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
            allocated_tables=[
                AllocatedTableRead.model_validate(allocation.table)
                for allocation in reservation.reservation_tables
            ],
        )


class ReservationCreateResponse(BaseModel):
    """201 — reserva criada + mesas alocadas."""

    reservation: ReservationRead
    allocated_tables: list[AllocatedTableRead]


class ReservationListResponse(BaseModel):
    items: list[ReservationRead]
    limit: int
    offset: int
    total: int


class AvailabilityResponse(BaseModel):
    """GET /reservations/availability (docs/API_SPEC.md §7).

    `status` "partial" e `conflicting_slots` dependem da grade de slots/horário de
    funcionamento (D10, aberto) — não são calculados nesta fase (lista vazia).
    """

    status: Literal["available", "unavailable", "partial"]
    conflicting_slots: list = Field(default_factory=list)
    estimated_tables: int
