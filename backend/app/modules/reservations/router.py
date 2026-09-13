"""Router do módulo `reservations`.

Camada de transporte apenas (docs/ARCHITECTURE.md §4). Contratos em docs/API_SPEC.md §7.
O `user_id` nunca vem do corpo: é obtido do usuário autenticado (dependência existente).
"""

from __future__ import annotations

from datetime import date, time
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.modules.reservations import service
from app.modules.reservations.model import ReservationStatus
from app.modules.reservations.schemas import (
    AvailabilityResponse,
    ReservationCancelRequest,
    ReservationCreate,
    ReservationCreateResponse,
    ReservationListResponse,
    ReservationRead,
    ReservationStatusUpdate,
    ReservationUpdate,
)
from app.modules.users.model import User, UserRole

router = APIRouter(prefix="/reservations", tags=["reservations"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/availability",
    response_model=AvailabilityResponse,
    summary="Disponibilidade",
)
def check_availability(
    restaurant_id: UUID = Query(...),
    date: date = Query(...),
    start_time: time = Query(...),
    people_count: int = Query(..., ge=1),
    duration_minutes: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.CUSTOMER)),
) -> AvailabilityResponse:
    status, estimated_tables = service.check_availability(
        db,
        restaurant_id=restaurant_id,
        reservation_date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
        people_count=people_count,
    )
    return AvailabilityResponse(
        status=status, conflicting_slots=[], estimated_tables=estimated_tables
    )


@router.post(
    "",
    response_model=ReservationCreateResponse,
    status_code=201,
    summary="Criar reserva",
)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
) -> ReservationCreateResponse:
    reservation = service.create_reservation(
        db,
        user=current_user,
        restaurant_id=payload.restaurant_id,
        reservation_date=payload.date,
        start_time=payload.start_time,
        duration_minutes=payload.duration_minutes,
        people_count=payload.people_count,
        notes=payload.notes,
    )
    read = ReservationRead.from_reservation(reservation)
    return ReservationCreateResponse(reservation=read, allocated_tables=read.allocated_tables)


@router.get("", response_model=ReservationListResponse, summary="Listar reservas")
def list_reservations(
    restaurant_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None, description="ADMIN (ignorado para CUSTOMER)"),
    status: ReservationStatus | None = Query(default=None),
    date: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationListResponse:
    items, total = service.list_reservations(
        db,
        user=current_user,
        restaurant_id=restaurant_id,
        user_id=user_id,
        status=status,
        on_date=date,
        limit=limit,
        offset=offset,
    )
    return ReservationListResponse(
        items=[ReservationRead.from_reservation(r) for r in items],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.get(
    "/{reservation_id}", response_model=ReservationRead, summary="Detalhe da reserva"
)
def get_reservation(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationRead:
    reservation = service.get_reservation_for_user(db, current_user, reservation_id)
    return ReservationRead.from_reservation(reservation)


@router.patch(
    "/{reservation_id}", response_model=ReservationRead, summary="Editar reserva"
)
def update_reservation(
    reservation_id: UUID,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationRead:
    reservation = service.update_reservation(
        db,
        user=current_user,
        reservation_id=reservation_id,
        changes=payload.model_dump(exclude_unset=True),
    )
    return ReservationRead.from_reservation(reservation)


@router.delete(
    "/{reservation_id}", response_model=ReservationRead, summary="Cancelar reserva"
)
def cancel_reservation(
    reservation_id: UUID,
    payload: ReservationCancelRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationRead:
    reservation = service.cancel_reservation(
        db, user=current_user, reservation_id=reservation_id
    )
    return ReservationRead.from_reservation(reservation)


# ---------------------------------------------------------------------------
# Admin — reservas do restaurante (prefixo /admin)
# ---------------------------------------------------------------------------
@admin_router.get(
    "/reservations", response_model=ReservationListResponse, summary="Listar reservas (admin)"
)
def admin_list_reservations(
    restaurant_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    status: ReservationStatus | None = Query(default=None),
    date: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> ReservationListResponse:
    items, total = service.list_reservations(
        db,
        user=current_user,
        restaurant_id=restaurant_id,
        user_id=user_id,
        status=status,
        on_date=date,
        limit=limit,
        offset=offset,
    )
    return ReservationListResponse(
        items=[ReservationRead.from_reservation(r) for r in items],
        limit=limit,
        offset=offset,
        total=total,
    )


@admin_router.patch(
    "/reservations/{reservation_id}/status",
    response_model=ReservationRead,
    summary="Mudar status (admin)",
)
def admin_change_status(
    reservation_id: UUID,
    payload: ReservationStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> ReservationRead:
    reservation = service.change_status(
        db, reservation_id=reservation_id, target_status=payload.status
    )
    return ReservationRead.from_reservation(reservation)
