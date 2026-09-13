"""Service do módulo `reservations` — casos de uso de reserva (regras de negócio).

Centraliza validação, disponibilidade, capacidade, alocação, overlap, criação, alteração
e cancelamento (docs/ARCHITECTURE.md §4; ADR-010/011/005). O router nunca decide regra.

Reutilização: `check_availability` e `create_reservation`/`update_reservation` compartilham
`_validate_request` + capacidade + cálculo de ocupação — **não** há duas implementações da
mesma regra.

Transacionalidade e concorrência (ADR-011): a alocação reserva as mesas elegíveis com
`SELECT ... FOR UPDATE` (repository) e só então checa ocupação; toda a operação ocorre em
uma transação, com `commit` no fim e `rollback` em qualquer erro.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.reservations import capacity, policies
from app.modules.reservations import repository as reservations_repository
from app.modules.reservations.model import Reservation, ReservationStatus
from app.modules.restaurants import repository as restaurants_repository
from app.modules.users.model import User, UserRole


def _load_restaurant_and_settings(db: Session, restaurant_id: UUID):
    """Carrega o restaurante (ativo) e sua configuração 1:1; 404/409 quando indisponível."""
    restaurant = restaurants_repository.get_restaurant(db, restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")
    if not restaurant.is_active:
        raise ConflictError("Restaurant is not active")
    settings = restaurants_repository.get_settings(db, restaurant_id)
    if settings is None:
        raise NotFoundError("Restaurant settings not found")
    return restaurant, settings


def _validate_request(
    settings,
    *,
    reservation_date: date,
    start_time: time,
    duration_minutes: int,
    people_count: int,
    now: datetime,
) -> tuple[datetime, datetime]:
    """Valida duração, antecedência e nº de pessoas contra a configuração (ADR-010)."""
    policies.ensure_duration_allowed(
        duration_minutes,
        minimum=settings.reservation_min_duration_minutes,
        maximum=settings.reservation_max_duration_minutes,
        step=settings.reservation_duration_step_minutes,
    )
    start_at, end_at = policies.reservation_interval(
        reservation_date, start_time, duration_minutes
    )
    policies.ensure_lead_time(
        start_at,
        now=now,
        min_lead_minutes=settings.min_booking_lead_minutes,
        max_lead_days=settings.max_booking_lead_days,
    )
    policies.ensure_people_count_allowed(
        people_count,
        minimum=settings.min_people_per_reservation,
        maximum=settings.max_people_per_reservation,
    )
    return start_at, end_at


def _required_tables(db: Session, restaurant_id: UUID, people_count: int) -> int:
    rules = restaurants_repository.list_active_capacity_rules(db, restaurant_id)
    return capacity.resolve_tables_required(people_count, rules)


def _allocate(
    db: Session,
    *,
    restaurant,
    settings,
    reservation_date: date,
    start_time: time,
    duration_minutes: int,
    people_count: int,
    exclude_reservation_id: UUID | None = None,
):
    """Valida, calcula mesas necessárias e seleciona mesas livres (bloqueando as elegíveis)."""
    now = datetime.now(timezone.utc)
    start_at, end_at = _validate_request(
        settings,
        reservation_date=reservation_date,
        start_time=start_time,
        duration_minutes=duration_minutes,
        people_count=people_count,
        now=now,
    )
    required = _required_tables(db, restaurant.id, people_count)

    candidates = reservations_repository.lock_eligible_tables(db, restaurant.id)
    occupied = reservations_repository.table_ids_occupied_during(
        db,
        restaurant_id=restaurant.id,
        start_at=start_at,
        end_at=end_at,
        candidate_table_ids=[table.id for table in candidates],
        exclude_reservation_id=exclude_reservation_id,
    )
    return capacity.select_tables(candidates, occupied, required)


def check_availability(
    db: Session,
    *,
    restaurant_id: UUID,
    reservation_date: date,
    start_time: time,
    duration_minutes: int | None,
    people_count: int,
) -> tuple[str, int]:
    """Disponibilidade (read-only) reutilizando as mesmas regras da criação.

    `duration_minutes` ausente usa a duração mínima configurada (API_SPEC §7). Retorna
    `(status, estimated_tables)`. `status` "partial"/`conflicting_slots` dependem da grade
    de slots (D10 aberto), portanto não são calculados aqui.
    """
    restaurant, settings = _load_restaurant_and_settings(db, restaurant_id)
    if duration_minutes is None:
        duration_minutes = settings.reservation_min_duration_minutes
    now = datetime.now(timezone.utc)
    start_at, end_at = _validate_request(
        settings,
        reservation_date=reservation_date,
        start_time=start_time,
        duration_minutes=duration_minutes,
        people_count=people_count,
        now=now,
    )
    required = _required_tables(db, restaurant.id, people_count)

    candidates = reservations_repository.list_eligible_tables(db, restaurant.id)
    occupied = reservations_repository.table_ids_occupied_during(
        db,
        restaurant_id=restaurant.id,
        start_at=start_at,
        end_at=end_at,
        candidate_table_ids=[table.id for table in candidates],
    )
    free = capacity.available_tables(candidates, occupied)
    status = "available" if len(free) >= required else "unavailable"
    return status, required


def create_reservation(
    db: Session,
    *,
    user: User,
    restaurant_id: UUID,
    reservation_date: date,
    start_time: time,
    duration_minutes: int,
    people_count: int,
    notes: str | None,
) -> Reservation:
    """Cria a reserva (status `PENDING`) e aloca as mesas — em uma única transação.

    O `user_id` vem do usuário autenticado (nunca do corpo da requisição — API_SPEC §7).
    """
    restaurant, settings = _load_restaurant_and_settings(db, restaurant_id)
    try:
        tables = _allocate(
            db,
            restaurant=restaurant,
            settings=settings,
            reservation_date=reservation_date,
            start_time=start_time,
            duration_minutes=duration_minutes,
            people_count=people_count,
        )
        reservation = reservations_repository.create_reservation(
            db,
            user_id=user.id,
            restaurant_id=restaurant.id,
            reservation_date=reservation_date,
            start_time=start_time,
            duration_minutes=duration_minutes,
            people_count=people_count,
            status=ReservationStatus.PENDING,
            notes=notes,
        )
        reservations_repository.allocate_tables(
            db, reservation, tables, datetime.now(timezone.utc)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return reservations_repository.get_reservation(db, reservation.id)


def update_reservation(
    db: Session, *, user: User, reservation_id: UUID, changes: dict
) -> Reservation:
    """Edita a reserva (se `PENDING`/`CONFIRMED`) revalidando e re-alocando se necessário.

    A re-alocação substitui as `ReservationTable` antigas — não se mantêm mesas que
    a nova quantidade de pessoas não exige (API_SPEC §7).
    """
    reservation = get_reservation_for_user(db, user, reservation_id)
    if reservation.status not in policies.EDITABLE_STATUSES:
        raise ConflictError(
            f"Reservation in status {reservation.status.value} cannot be edited"
        )
    restaurant, settings = _load_restaurant_and_settings(db, reservation.restaurant_id)

    new_date = changes.get("date") or reservation.date
    new_start = changes.get("start_time") or reservation.start_time
    new_duration = changes.get("duration_minutes") or reservation.duration_minutes
    new_people = changes.get("people_count") or reservation.people_count
    allocation_changed = (
        new_date,
        new_start,
        new_duration,
        new_people,
    ) != (
        reservation.date,
        reservation.start_time,
        reservation.duration_minutes,
        reservation.people_count,
    )

    try:
        if allocation_changed:
            tables = _allocate(
                db,
                restaurant=restaurant,
                settings=settings,
                reservation_date=new_date,
                start_time=new_start,
                duration_minutes=new_duration,
                people_count=new_people,
                exclude_reservation_id=reservation.id,
            )
            reservations_repository.clear_allocations(db, reservation)
            reservations_repository.allocate_tables(
                db, reservation, tables, datetime.now(timezone.utc)
            )
            reservation.date = new_date
            reservation.start_time = new_start
            reservation.duration_minutes = new_duration
            reservation.people_count = new_people
        if "notes" in changes:
            reservation.notes = changes["notes"]
        db.commit()
    except Exception:
        db.rollback()
        raise
    return reservations_repository.get_reservation(db, reservation.id)


def cancel_reservation(db: Session, *, user: User, reservation_id: UUID) -> Reservation:
    """Cancelamento negocial dentro da janela configurada (R12/R13/R14 — ADR-010).

    Não há exclusão física: `status = CANCELLED`, `cancelled_at`/`cancelled_by` preenchidos
    e as `ReservationTable` preservadas como histórico (API_SPEC §7). A janela de
    cancelamento é aplicada a CUSTOMER e ADMIN; o ADMIN dispõe do endpoint de status
    (`PATCH /admin/reservations/{id}/status`) para mudanças operacionais.
    """
    reservation = get_reservation_for_user(db, user, reservation_id)
    if reservation.status not in policies.CANCELLABLE_STATUSES:
        raise ConflictError(
            f"Reservation in status {reservation.status.value} cannot be cancelled"
        )
    _, settings = _load_restaurant_and_settings(db, reservation.restaurant_id)
    now = datetime.now(timezone.utc)
    if not policies.can_cancel(
        reservation.start_at,
        now=now,
        cancellation_window_minutes=settings.cancellation_window_minutes,
    ):
        raise ConflictError("Cancellation window has passed")

    reservation.status = ReservationStatus.CANCELLED
    reservation.cancelled_at = now
    reservation.cancelled_by = user.role
    db.commit()
    return reservations_repository.get_reservation(db, reservation.id)


def get_reservation_for_user(db: Session, user: User, reservation_id: UUID) -> Reservation:
    """Carrega a reserva garantindo autorização: proprietário ou `ADMIN`."""
    reservation = reservations_repository.get_reservation(db, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")
    if user.role != UserRole.ADMIN and reservation.user_id != user.id:
        raise ForbiddenError("You cannot access this reservation")
    return reservation


def list_reservations(
    db: Session,
    *,
    user: User,
    restaurant_id: UUID | None = None,
    user_id: UUID | None = None,
    status: ReservationStatus | None = None,
    on_date: date | None = None,
    limit: int,
    offset: int,
) -> tuple[list[Reservation], int]:
    """Lista reservas: CUSTOMER vê só as próprias; ADMIN vê todas (API_SPEC §7)."""
    if user.role != UserRole.ADMIN:
        user_id = user.id
    return reservations_repository.list_reservations(
        db,
        user_id=user_id,
        restaurant_id=restaurant_id,
        status=status,
        on_date=on_date,
        limit=limit,
        offset=offset,
    )


def change_status(
    db: Session, *, reservation_id: UUID, target_status: ReservationStatus
) -> Reservation:
    """Admin — muda o status respeitando as transições documentadas (DOMAIN_SPEC §4.2)."""
    reservation = reservations_repository.get_reservation(db, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")
    if reservation.status == target_status:
        return reservation
    policies.ensure_transition(reservation.status, target_status)
    reservation.status = target_status
    if target_status == ReservationStatus.CANCELLED:
        reservation.cancelled_at = datetime.now(timezone.utc)
        reservation.cancelled_by = UserRole.ADMIN
    db.commit()
    return reservations_repository.get_reservation(db, reservation.id)
