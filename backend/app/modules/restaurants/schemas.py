"""Schemas (DTOs) do módulo `restaurants`.

Separação request/response: a entidade ORM nunca é exposta diretamente. Os nomes
públicos de settings seguem docs/API_SPEC.md §6 e são mapeados para as colunas do
domínio (DOMAIN_SPEC §2.3) pelo service.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Restaurant
# ---------------------------------------------------------------------------
class RestaurantCreate(BaseModel):
    """Admin — cria restaurante (e a configuração 1:1 com os defaults do ADR-010)."""

    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=140)
    phone: str | None = Field(default=None, max_length=32)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=140)
    phone: str | None = Field(default=None, max_length=32)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str | None
    phone: str | None
    description: str | None
    address: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# RestaurantSettings
# ---------------------------------------------------------------------------
class RestaurantSettingsPublic(BaseModel):
    """Configuração como exposta ao cliente (docs/API_SPEC.md §6)."""

    min_duration_minutes: int
    max_duration_minutes: int
    duration_step_minutes: int
    min_people: int
    max_people: int
    cancellation_window_minutes: int
    min_booking_lead_minutes: int
    max_booking_lead_days: int
    preorder_enabled: bool

    @classmethod
    def from_settings(cls, settings) -> "RestaurantSettingsPublic":
        return cls(
            min_duration_minutes=settings.reservation_min_duration_minutes,
            max_duration_minutes=settings.reservation_max_duration_minutes,
            duration_step_minutes=settings.reservation_duration_step_minutes,
            min_people=settings.min_people_per_reservation,
            max_people=settings.max_people_per_reservation,
            cancellation_window_minutes=settings.cancellation_window_minutes,
            min_booking_lead_minutes=settings.min_booking_lead_minutes,
            max_booking_lead_days=settings.max_booking_lead_days,
            preorder_enabled=settings.preorder_enabled,
        )


class RestaurantSettingsUpdate(BaseModel):
    """Admin — atualização parcial de `RestaurantSettings` (nomes públicos)."""

    min_duration_minutes: int | None = Field(default=None, ge=1)
    max_duration_minutes: int | None = Field(default=None, ge=1)
    duration_step_minutes: int | None = Field(default=None, ge=1)
    min_people: int | None = Field(default=None, ge=1)
    max_people: int | None = Field(default=None, ge=1)
    cancellation_window_minutes: int | None = Field(default=None, ge=0)
    min_booking_lead_minutes: int | None = Field(default=None, ge=0)
    max_booking_lead_days: int | None = Field(default=None, ge=1)
    preorder_enabled: bool | None = None


class RestaurantDetailRead(RestaurantRead):
    """GET /restaurants/{id} — restaurante + configurações resumidas."""

    settings: RestaurantSettingsPublic | None


class RestaurantListResponse(BaseModel):
    items: list[RestaurantRead]
    limit: int
    offset: int
    total: int


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------
class TableCreate(BaseModel):
    restaurant_id: UUID
    label: str = Field(min_length=1, max_length=40)
    capacity: int = Field(ge=1)
    position_x: float | None = None
    position_y: float | None = None
    position_z: float | None = None
    is_locked: bool = False


class TableUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=40)
    capacity: int | None = Field(default=None, ge=1)
    position_x: float | None = None
    position_y: float | None = None
    position_z: float | None = None
    is_locked: bool | None = None
    is_active: bool | None = None


class TableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    label: str
    capacity: int
    is_locked: bool
    position_x: float | None
    position_y: float | None
    position_z: float | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TableListResponse(BaseModel):
    items: list[TableRead]


# ---------------------------------------------------------------------------
# CapacityRule
# ---------------------------------------------------------------------------
class CapacityRuleCreate(BaseModel):
    restaurant_id: UUID
    min_people: int = Field(ge=1)
    max_people: int = Field(ge=1)
    tables_required: int = Field(ge=1)
    is_active: bool = True


class CapacityRuleUpdate(BaseModel):
    min_people: int | None = Field(default=None, ge=1)
    max_people: int | None = Field(default=None, ge=1)
    tables_required: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class CapacityRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    min_people: int
    max_people: int
    tables_required: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CapacityRuleListResponse(BaseModel):
    items: list[CapacityRuleRead]
