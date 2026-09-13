"""Routers do módulo `restaurants`.

Camada de transporte apenas: valida schema, chama o service e serializa a resposta
(docs/ARCHITECTURE.md §4). Contratos conforme docs/API_SPEC.md §6/§8/§14.

Nota: `POST/PATCH /restaurants` e `GET /admin/capacity-rules` são adições mínimas
desta fase (necessárias para operar e testar; ver ADR-017), documentadas em API_SPEC §6/§14.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.modules.restaurants import service
from app.modules.restaurants.schemas import (
    CapacityRuleCreate,
    CapacityRuleListResponse,
    CapacityRuleRead,
    CapacityRuleUpdate,
    RestaurantCreate,
    RestaurantDetailRead,
    RestaurantListResponse,
    RestaurantRead,
    RestaurantSettingsPublic,
    RestaurantSettingsUpdate,
    RestaurantUpdate,
    TableCreate,
    TableListResponse,
    TableRead,
    TableUpdate,
)
from app.modules.users.model import User, UserRole

router = APIRouter(prefix="/restaurants", tags=["restaurants"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])
tables_router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("", response_model=RestaurantListResponse, summary="Listar restaurantes")
def list_restaurants(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RestaurantListResponse:
    items, total = service.list_restaurants(db, limit=limit, offset=offset)
    return RestaurantListResponse(
        items=[RestaurantRead.model_validate(r) for r in items],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.post(
    "",
    response_model=RestaurantRead,
    status_code=201,
    summary="Criar restaurante (admin)",
)
def create_restaurant(
    payload: RestaurantCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> RestaurantRead:
    restaurant = service.create_restaurant(
        db,
        name=payload.name,
        slug=payload.slug,
        phone=payload.phone,
        description=payload.description,
        address=payload.address,
        is_active=payload.is_active,
    )
    return RestaurantRead.model_validate(restaurant)


@router.get("/{restaurant_id}", response_model=RestaurantDetailRead, summary="Detalhe")
def get_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RestaurantDetailRead:
    restaurant = service.get_restaurant_or_404(db, restaurant_id)
    settings = restaurant.settings
    # Construído explicitamente: o campo `settings` usa os nomes públicos e é mapeado
    # a partir do ORM por `from_settings` (não se valida o objeto ORM direto).
    return RestaurantDetailRead(
        **RestaurantRead.model_validate(restaurant).model_dump(),
        settings=RestaurantSettingsPublic.from_settings(settings) if settings else None,
    )


@router.patch(
    "/{restaurant_id}", response_model=RestaurantRead, summary="Atualizar restaurante (admin)"
)
def update_restaurant(
    restaurant_id: UUID,
    payload: RestaurantUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> RestaurantRead:
    restaurant = service.update_restaurant(
        db, restaurant_id, changes=payload.model_dump(exclude_unset=True)
    )
    return RestaurantRead.model_validate(restaurant)


@router.get(
    "/{restaurant_id}/settings",
    response_model=RestaurantSettingsPublic,
    summary="Configurações públicas",
)
def get_settings(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RestaurantSettingsPublic:
    settings = service.get_settings_or_404(db, restaurant_id)
    return RestaurantSettingsPublic.from_settings(settings)


@router.get(
    "/{restaurant_id}/tables",
    response_model=TableListResponse,
    summary="Listar mesas",
)
def list_tables(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TableListResponse:
    # Clientes veem apenas mesas não bloqueadas; o ADMIN vê todas (API_SPEC §8).
    include_locked = current_user.role == UserRole.ADMIN
    tables = service.list_tables(db, restaurant_id, include_locked=include_locked)
    return TableListResponse(items=[TableRead.model_validate(t) for t in tables])


# ---------------------------------------------------------------------------
# Admin — configuração e regras de capacidade (prefixo /admin)
# ---------------------------------------------------------------------------
@admin_router.patch(
    "/restaurants/{restaurant_id}/settings",
    response_model=RestaurantSettingsPublic,
    summary="Editar configuração (admin)",
)
def update_settings(
    restaurant_id: UUID,
    payload: RestaurantSettingsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> RestaurantSettingsPublic:
    settings = service.update_settings(
        db, restaurant_id, changes=payload.model_dump(exclude_unset=True)
    )
    return RestaurantSettingsPublic.from_settings(settings)


@admin_router.get(
    "/capacity-rules",
    response_model=CapacityRuleListResponse,
    summary="Listar regras de capacidade (admin)",
)
def list_capacity_rules(
    restaurant_id: UUID = Query(...),
    include_inactive: bool = Query(default=True),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> CapacityRuleListResponse:
    rules = service.list_capacity_rules(
        db, restaurant_id, include_inactive=include_inactive
    )
    return CapacityRuleListResponse(
        items=[CapacityRuleRead.model_validate(r) for r in rules]
    )


@admin_router.post(
    "/capacity-rules",
    response_model=CapacityRuleRead,
    status_code=201,
    summary="Criar regra de capacidade (admin)",
)
def create_capacity_rule(
    payload: CapacityRuleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> CapacityRuleRead:
    rule = service.create_capacity_rule(
        db,
        restaurant_id=payload.restaurant_id,
        min_people=payload.min_people,
        max_people=payload.max_people,
        tables_required=payload.tables_required,
        is_active=payload.is_active,
    )
    return CapacityRuleRead.model_validate(rule)


@admin_router.patch(
    "/capacity-rules/{rule_id}",
    response_model=CapacityRuleRead,
    summary="Editar regra de capacidade (admin)",
)
def update_capacity_rule(
    rule_id: UUID,
    payload: CapacityRuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> CapacityRuleRead:
    rule = service.update_capacity_rule(
        db, rule_id, changes=payload.model_dump(exclude_unset=True)
    )
    return CapacityRuleRead.model_validate(rule)


# ---------------------------------------------------------------------------
# Admin — mesas (prefixo /tables)
# ---------------------------------------------------------------------------
@tables_router.post(
    "", response_model=TableRead, status_code=201, summary="Criar mesa (admin)"
)
def create_table(
    payload: TableCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> TableRead:
    table = service.create_table(
        db,
        restaurant_id=payload.restaurant_id,
        label=payload.label,
        capacity=payload.capacity,
        position_x=payload.position_x,
        position_y=payload.position_y,
        position_z=payload.position_z,
        is_locked=payload.is_locked,
    )
    return TableRead.model_validate(table)


@tables_router.patch(
    "/{table_id}", response_model=TableRead, summary="Atualizar mesa (admin)"
)
def update_table(
    table_id: UUID,
    payload: TableUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> TableRead:
    table = service.update_table(
        db, table_id, changes=payload.model_dump(exclude_unset=True)
    )
    return TableRead.model_validate(table)
