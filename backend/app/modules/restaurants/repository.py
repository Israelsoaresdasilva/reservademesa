"""Repository do módulo `restaurants` — fronteira de acesso a dados.

Camada conforme docs/ARCHITECTURE.md §4 (repository). Sem regras de negócio: apenas
consultas e helpers de persistência usados pelo `service`.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.restaurants.model import CapacityRule, Restaurant, RestaurantSettings, Table


def get_restaurant(db: Session, restaurant_id: UUID) -> Restaurant | None:
    return db.get(Restaurant, restaurant_id)


def get_restaurant_by_slug(db: Session, slug: str) -> Restaurant | None:
    return db.scalar(select(Restaurant).where(Restaurant.slug == slug))


def lock_restaurant(db: Session, restaurant_id: UUID) -> Restaurant | None:
    """Carrega o restaurante com `SELECT ... FOR UPDATE` (serializa escritas por restaurante)."""
    return db.get(Restaurant, restaurant_id, with_for_update=True)


def list_restaurants(db: Session, *, limit: int, offset: int) -> list[Restaurant]:
    stmt = (
        select(Restaurant)
        .order_by(Restaurant.created_at, Restaurant.id)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


def count_restaurants(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Restaurant)) or 0


def get_settings(db: Session, restaurant_id: UUID) -> RestaurantSettings | None:
    stmt = select(RestaurantSettings).where(
        RestaurantSettings.restaurant_id == restaurant_id
    )
    return db.scalar(stmt)


def get_table(db: Session, table_id: UUID) -> Table | None:
    return db.get(Table, table_id)


def get_table_by_label(db: Session, restaurant_id: UUID, label: str) -> Table | None:
    stmt = select(Table).where(
        Table.restaurant_id == restaurant_id,
        func.lower(Table.label) == label.strip().lower(),
    )
    return db.scalar(stmt)


def list_tables(
    db: Session, restaurant_id: UUID, *, include_locked: bool
) -> list[Table]:
    stmt = select(Table).where(Table.restaurant_id == restaurant_id)
    if not include_locked:
        stmt = stmt.where(Table.is_locked.is_(False))
    stmt = stmt.order_by(Table.label, Table.id)
    return list(db.scalars(stmt))


def get_capacity_rule(db: Session, rule_id: UUID) -> CapacityRule | None:
    return db.get(CapacityRule, rule_id)


def list_capacity_rules(
    db: Session, restaurant_id: UUID, *, include_inactive: bool = True
) -> list[CapacityRule]:
    stmt = select(CapacityRule).where(CapacityRule.restaurant_id == restaurant_id)
    if not include_inactive:
        stmt = stmt.where(CapacityRule.is_active.is_(True))
    stmt = stmt.order_by(CapacityRule.min_people, CapacityRule.id)
    return list(db.scalars(stmt))


def list_active_capacity_rules(db: Session, restaurant_id: UUID) -> list[CapacityRule]:
    return list_capacity_rules(db, restaurant_id, include_inactive=False)
