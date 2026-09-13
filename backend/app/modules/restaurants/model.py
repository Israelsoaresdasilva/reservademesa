"""ORM models do módulo `restaurants`.

Modelos fiéis a docs/DOMAIN_SPEC.md:
- §2.2 `Restaurant`
- §2.3 `RestaurantSettings` (1:1 com `Restaurant`)
- §2.4 `Table` (mesa física, alocável; `is_locked` exclui da alocação — R8)
- §2.5 `CapacityRule` (faixa de pessoas → nº de mesas — ADR-005)

Observações de implementação (Fase 3):
- Campos `[TBD]` de `RestaurantSettings` (`opening_hours` — D10, `review_allowed_after_hours`
  — Fase 6) **não** são modelados nesta fase (D10 permanece aberto; decisão de escopo).
- `Table` reside no módulo `restaurants` (recurso do restaurante); `ReservationTable`
  (associação com reservas) reside no módulo `reservations`.
- Enum de role reutilizado de `users` apenas no módulo `reservations`.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# ---------------------------------------------------------------------------
# Defaults de reserva (ADR-010). São **valores de configuração persistidos** por
# restaurante (criados em `RestaurantSettings`), NÃO constantes rígidas do domínio:
# o service sempre lê a configuração do restaurante, nunca estes valores diretamente.
# ---------------------------------------------------------------------------
DEFAULT_CANCELLATION_WINDOW_MINUTES = 60
DEFAULT_MIN_BOOKING_LEAD_MINUTES = 60
DEFAULT_MAX_BOOKING_LEAD_DAYS = 90
DEFAULT_RESERVATION_MIN_DURATION_MINUTES = 30
DEFAULT_RESERVATION_MAX_DURATION_MINUTES = 180
DEFAULT_RESERVATION_DURATION_STEP_MINUTES = 30

# Limites de pessoas por reserva — DOMAIN_SPEC §2.3 marca `min_people` como `[PROPOSTA]`;
# os valores abaixo são defaults de implementação (configuráveis pelo ADMIN), não uma
# decisão de domínio fechada.
DEFAULT_MIN_PEOPLE_PER_RESERVATION = 1
DEFAULT_MAX_PEOPLE_PER_RESERVATION = 20


class Restaurant(Base):
    """Restaurante (docs/DOMAIN_SPEC.md §2.2). O modelo suporta N (D3 aberto)."""

    __tablename__ = "restaurants"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str | None] = mapped_column(
        String(140), nullable=True, unique=True, index=True
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
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

    settings: Mapped[RestaurantSettings | None] = relationship(
        back_populates="restaurant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    tables: Mapped[list[Table]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )
    capacity_rules: Mapped[list[CapacityRule]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )
    # Referência por string para evitar import cíclico entre módulos
    # (`Reservation` vive em `reservations`).
    reservations: Mapped[list["Reservation"]] = relationship(  # noqa: F821
        back_populates="restaurant",
    )


class RestaurantSettings(Base):
    """Configuração operacional do restaurante (docs/DOMAIN_SPEC.md §2.3).

    1:1 com `Restaurant` (unique em `restaurant_id`). Os defaults seguem ADR-010 e
    são configuráveis pelo ADMIN (nunca constantes do service).
    """

    __tablename__ = "restaurant_settings"
    __table_args__ = (
        CheckConstraint(
            "cancellation_window_minutes >= 0",
            name="ck_restaurant_settings_cancellation_window",
        ),
        CheckConstraint(
            "min_booking_lead_minutes >= 0",
            name="ck_restaurant_settings_min_lead",
        ),
        CheckConstraint(
            "max_booking_lead_days >= 1",
            name="ck_restaurant_settings_max_lead_days",
        ),
        CheckConstraint(
            "min_people_per_reservation >= 1",
            name="ck_restaurant_settings_min_people",
        ),
        CheckConstraint(
            "max_people_per_reservation >= min_people_per_reservation",
            name="ck_restaurant_settings_people_range",
        ),
        CheckConstraint(
            "reservation_min_duration_minutes >= 1",
            name="ck_restaurant_settings_min_duration",
        ),
        CheckConstraint(
            "reservation_max_duration_minutes >= reservation_min_duration_minutes",
            name="ck_restaurant_settings_duration_range",
        ),
        CheckConstraint(
            "reservation_duration_step_minutes BETWEEN "
            "reservation_min_duration_minutes AND reservation_max_duration_minutes",
            name="ck_restaurant_settings_duration_step",
        ),
        UniqueConstraint(
            "restaurant_id", name="uq_restaurant_settings_restaurant"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )
    cancellation_window_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_CANCELLATION_WINDOW_MINUTES
    )
    min_booking_lead_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_MIN_BOOKING_LEAD_MINUTES
    )
    max_booking_lead_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_MAX_BOOKING_LEAD_DAYS
    )
    max_people_per_reservation: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_MAX_PEOPLE_PER_RESERVATION
    )
    min_people_per_reservation: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_MIN_PEOPLE_PER_RESERVATION
    )
    reservation_min_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_RESERVATION_MIN_DURATION_MINUTES
    )
    reservation_max_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_RESERVATION_MAX_DURATION_MINUTES
    )
    reservation_duration_step_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_RESERVATION_DURATION_STEP_MINUTES
    )
    preorder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    restaurant: Mapped[Restaurant] = relationship(back_populates="settings")


class Table(Base):
    """Mesa física do salão (docs/DOMAIN_SPEC.md §2.4).

    `is_locked = true` exclui a mesa da alocação automática (R8); `is_active = false`
    a retira da operação. Somente mesas ativas e não bloqueadas são elegíveis.
    """

    __tablename__ = "tables"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "label", name="uq_tables_restaurant_label"),
        CheckConstraint("capacity >= 1", name="ck_tables_capacity_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(40), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_z: Mapped[float | None] = mapped_column(Float, nullable=True)
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

    restaurant: Mapped[Restaurant] = relationship(back_populates="tables")


class CapacityRule(Base):
    """Faixa de pessoas → nº de mesas necessárias (docs/DOMAIN_SPEC.md §2.5 — ADR-005).

    As faixas de um mesmo restaurante não podem se sobrepor; a validação é feita no
    service (`restaurants.service`) com bloqueio da linha do restaurante.
    """

    __tablename__ = "capacity_rules"
    __table_args__ = (
        CheckConstraint("min_people >= 1", name="ck_capacity_rules_min_people"),
        CheckConstraint("max_people >= min_people", name="ck_capacity_rules_range"),
        CheckConstraint("tables_required >= 1", name="ck_capacity_rules_tables_required"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    min_people: Mapped[int] = mapped_column(Integer, nullable=False)
    max_people: Mapped[int] = mapped_column(Integer, nullable=False)
    tables_required: Mapped[int] = mapped_column(Integer, nullable=False)
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

    restaurant: Mapped[Restaurant] = relationship(back_populates="capacity_rules")
