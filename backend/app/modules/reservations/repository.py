"""Repository do módulo `reservations` — fronteira de acesso a dados.

Camada conforme docs/ARCHITECTURE.md §4 (repository). Contém as consultas usadas para
disponibilidade/overlap e o **bloqueio das mesas candidatas** (`SELECT ... FOR UPDATE`).

Concorrência (ADR-011): `lock_eligible_tables` bloqueia as linhas de `tables` do
restaurante em ordem determinística antes de checar ocupação — duas transações que
disputem as mesmas mesas serializam e a segunda enxerga a alocação já confirmada.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.reservations import policies
from app.modules.reservations.model import (
    Reservation,
    ReservationStatus,
    ReservationTable,
)
from app.modules.restaurants.model import Table


def _with_allocations(statement):
    return statement.options(
        selectinload(Reservation.reservation_tables).selectinload(ReservationTable.table)
    )


def get_reservation(db: Session, reservation_id: UUID) -> Reservation | None:
    return db.scalar(
        _with_allocations(select(Reservation).where(Reservation.id == reservation_id))
    )


def list_reservations(
    db: Session,
    *,
    user_id: UUID | None = None,
    restaurant_id: UUID | None = None,
    status: ReservationStatus | None = None,
    on_date=None,
    limit: int,
    offset: int,
) -> tuple[list[Reservation], int]:
    conditions = []
    if user_id is not None:
        conditions.append(Reservation.user_id == user_id)
    if restaurant_id is not None:
        conditions.append(Reservation.restaurant_id == restaurant_id)
    if status is not None:
        conditions.append(Reservation.status == status)
    if on_date is not None:
        conditions.append(Reservation.date == on_date)

    total = (
        db.scalar(
            select(func.count()).select_from(Reservation).where(*conditions)
        )
        or 0
    )
    stmt = (
        _with_allocations(select(Reservation).where(*conditions))
        .order_by(
            Reservation.date.desc(),
            Reservation.start_time.desc(),
            Reservation.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt)), total


def create_reservation(
    db: Session,
    *,
    user_id: UUID,
    restaurant_id: UUID,
    reservation_date,
    start_time,
    duration_minutes: int,
    people_count: int,
    status: ReservationStatus,
    notes: str | None,
) -> Reservation:
    reservation = Reservation(
        user_id=user_id,
        restaurant_id=restaurant_id,
        date=reservation_date,
        start_time=start_time,
        duration_minutes=duration_minutes,
        people_count=people_count,
        status=status,
        notes=notes,
    )
    db.add(reservation)
    db.flush()
    return reservation


def _eligible_tables_statement(restaurant_id: UUID):
    return (
        select(Table)
        .where(
            Table.restaurant_id == restaurant_id,
            Table.is_active.is_(True),
            Table.is_locked.is_(False),
        )
        .order_by(Table.label, Table.id)
    )


def list_eligible_tables(db: Session, restaurant_id: UUID) -> list[Table]:
    """Mesas elegíveis (ativas e não bloqueadas) — leitura, sem bloqueio (disponibilidade)."""
    return list(db.scalars(_eligible_tables_statement(restaurant_id)))


def lock_eligible_tables(db: Session, restaurant_id: UUID) -> list[Table]:
    """Mesas ativas e não bloqueadas do restaurante, bloqueadas para alocação (`FOR UPDATE`)."""
    stmt = _eligible_tables_statement(restaurant_id).with_for_update()
    return list(db.scalars(stmt))


def table_ids_occupied_during(
    db: Session,
    *,
    restaurant_id: UUID,
    start_at: datetime,
    end_at: datetime,
    candidate_table_ids: list[UUID],
    exclude_reservation_id: UUID | None = None,
) -> set[UUID]:
    """Mesas ocupadas por reservas não canceladas que sobrepõem `[start_at, end_at)`."""
    candidates = set(candidate_table_ids)
    if not candidates:
        return set()

    stmt = (
        select(
            ReservationTable.table_id,
            Reservation.date,
            Reservation.start_time,
            Reservation.duration_minutes,
        )
        .join(Reservation, Reservation.id == ReservationTable.reservation_id)
        .where(
            Reservation.restaurant_id == restaurant_id,
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.date >= start_at.date() - timedelta(days=1),
            Reservation.date <= end_at.date() + timedelta(days=1),
        )
    )
    if exclude_reservation_id is not None:
        stmt = stmt.where(Reservation.id != exclude_reservation_id)

    occupied: set[UUID] = set()
    for table_id, res_date, res_start, res_duration in db.execute(stmt).all():
        if table_id not in candidates:
            continue
        existing_start = policies.combine_start_at(res_date, res_start)
        existing_end = existing_start + timedelta(minutes=res_duration)
        if policies.intervals_overlap(existing_start, existing_end, start_at, end_at):
            occupied.add(table_id)
    return occupied


def clear_allocations(db: Session, reservation: Reservation) -> None:
    for allocation in list(reservation.reservation_tables):
        db.delete(allocation)
    db.flush()


def allocate_tables(
    db: Session, reservation: Reservation, tables, allocated_at: datetime
) -> None:
    for table in tables:
        db.add(
            ReservationTable(
                reservation_id=reservation.id,
                table_id=table.id,
                allocated_at=allocated_at,
            )
        )
    db.flush()
