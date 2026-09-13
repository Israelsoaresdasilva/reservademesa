"""ORM models do módulo `reservations`.

Modelos fiéis a docs/DOMAIN_SPEC.md:
- §2.6 `Reservation` (núcleo do produto)
- §2.7 `ReservationTable` (associação N:N reserva ↔ mesas — ADR-004)
- §4.2 `ReservationStatus` (PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW)

Observações de implementação (Fase 3):
- A `Reservation` persiste `date` + `start_time` (fonte do domínio e do contrato da API),
  conforme DOMAIN_SPEC §2.6 / API_SPEC §7. O instante de início é exposto pela propriedade
  calculada `start_at` (UTC — ver `reservations.policies.combine_start_at`); não se faz
  comparação ingênua entre datetime *aware* e *naive*.
- `cancelled_by` reutiliza `UserRole` (users) — preenchido apenas no cancelamento (R12/R13).
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.users.model import UserRole


class ReservationStatus(str, enum.Enum):
    """Estados documentados (docs/DOMAIN_SPEC.md §4.2) — não inventar novos."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Reservation(Base):
    """Reserva de uma experiência no restaurante (docs/DOMAIN_SPEC.md §2.6)."""

    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_reservations_duration_positive"),
        CheckConstraint("people_count >= 1", name="ck_reservations_people_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(
            ReservationStatus,
            name="reservationstatus",
            native_enum=False,
            length=20,
            create_constraint=False,
        ),
        nullable=False,
        default=ReservationStatus.PENDING,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_by: Mapped[UserRole | None] = mapped_column(
        Enum(
            UserRole,
            name="userrole",
            native_enum=False,
            length=20,
            create_constraint=False,
        ),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship()  # noqa: F821
    restaurant: Mapped["Restaurant"] = relationship(  # noqa: F821
        back_populates="reservations"
    )
    reservation_tables: Mapped[list[ReservationTable]] = relationship(
        back_populates="reservation",
        cascade="all, delete-orphan",
    )

    @property
    def start_at(self) -> datetime:
        """Instante de início (UTC) derivado de `date` + `start_time` (DOMAIN_SPEC §5.1)."""
        return datetime.combine(self.date, self.start_time, tzinfo=timezone.utc)

    @property
    def end_at(self) -> datetime:
        """Instante de término (UTC) — intervalo `[start_at, end_at)` (ADR-011)."""
        return self.start_at + timedelta(minutes=self.duration_minutes)


class ReservationTable(Base):
    """Associação reserva ↔ mesas alocadas (docs/DOMAIN_SPEC.md §2.7 — ADR-004)."""

    __tablename__ = "reservation_tables"
    __table_args__ = (
        UniqueConstraint(
            "reservation_id", "table_id", name="uq_reservation_tables_reservation_table"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reservation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tables.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    reservation: Mapped[Reservation] = relationship(back_populates="reservation_tables")
    table: Mapped["Table"] = relationship()  # noqa: F821
