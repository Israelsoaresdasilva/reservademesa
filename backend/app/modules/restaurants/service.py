"""Service do módulo `restaurants` — casos de uso de restaurante, settings, mesas e regras.

Regras de negócio ficam aqui (docs/ARCHITECTURE.md §4), nunca nos routers. Ao criar um
restaurante, a configuração 1:1 (`RestaurantSettings`) é criada com os defaults do
ADR-010 — que são valores **persistidos e configuráveis**, não constantes do domínio.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, UnprocessableError
from app.modules.restaurants import repository as repository
from app.modules.restaurants.model import (
    CapacityRule,
    Restaurant,
    RestaurantSettings,
    Table,
)

# Nomes públicos de settings (API_SPEC §6) → colunas do domínio (DOMAIN_SPEC §2.3).
_SETTINGS_PUBLIC_TO_DOMAIN = {
    "min_duration_minutes": "reservation_min_duration_minutes",
    "max_duration_minutes": "reservation_max_duration_minutes",
    "duration_step_minutes": "reservation_duration_step_minutes",
    "min_people": "min_people_per_reservation",
    "max_people": "max_people_per_reservation",
    "cancellation_window_minutes": "cancellation_window_minutes",
    "min_booking_lead_minutes": "min_booking_lead_minutes",
    "max_booking_lead_days": "max_booking_lead_days",
    "preorder_enabled": "preorder_enabled",
}


def _ranges_overlap(a_min: int, a_max: int, b_min: int, b_max: int) -> bool:
    return a_min <= b_max and b_min <= a_max


# ---------------------------------------------------------------------------
# Restaurant
# ---------------------------------------------------------------------------
def list_restaurants(
    db: Session, *, limit: int, offset: int
) -> tuple[list[Restaurant], int]:
    return (
        repository.list_restaurants(db, limit=limit, offset=offset),
        repository.count_restaurants(db),
    )


def get_restaurant_or_404(db: Session, restaurant_id: UUID) -> Restaurant:
    restaurant = repository.get_restaurant(db, restaurant_id)
    if restaurant is None:
        raise NotFoundError("Restaurant not found")
    return restaurant


def create_restaurant(
    db: Session,
    *,
    name: str,
    slug: str | None,
    phone: str | None,
    description: str | None,
    address: str | None,
    is_active: bool,
) -> Restaurant:
    normalized_slug = slug.strip().lower() if slug else None
    if normalized_slug and repository.get_restaurant_by_slug(db, normalized_slug):
        raise ConflictError("Restaurant slug already in use")

    restaurant = Restaurant(
        name=name.strip(),
        slug=normalized_slug,
        phone=phone.strip() if phone else None,
        description=description,
        address=address.strip() if address else None,
        is_active=is_active,
    )
    # Configuração 1:1 criada com os defaults (ADR-010) — passa pelo ORM para
    # aplicar os valores default das colunas.
    restaurant.settings = RestaurantSettings()
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def update_restaurant(db: Session, restaurant_id: UUID, *, changes: dict) -> Restaurant:
    restaurant = get_restaurant_or_404(db, restaurant_id)
    if "slug" in changes and changes["slug"]:
        normalized_slug = changes["slug"].strip().lower()
        existing = repository.get_restaurant_by_slug(db, normalized_slug)
        if existing is not None and existing.id != restaurant.id:
            raise ConflictError("Restaurant slug already in use")
        changes["slug"] = normalized_slug
    for field, value in changes.items():
        if field in {"name", "address", "phone"} and isinstance(value, str):
            value = value.strip()
        setattr(restaurant, field, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


# ---------------------------------------------------------------------------
# RestaurantSettings
# ---------------------------------------------------------------------------
def get_settings_or_404(db: Session, restaurant_id: UUID) -> RestaurantSettings:
    get_restaurant_or_404(db, restaurant_id)
    settings = repository.get_settings(db, restaurant_id)
    if settings is None:
        raise NotFoundError("Restaurant settings not found")
    return settings


def _validate_settings_consistency(values: dict) -> None:
    """Garante as invariantes de `RestaurantSettings` (DOMAIN_SPEC §2.3) antes do commit."""
    min_duration = values["reservation_min_duration_minutes"]
    max_duration = values["reservation_max_duration_minutes"]
    step = values["reservation_duration_step_minutes"]
    min_people = values["min_people_per_reservation"]
    max_people = values["max_people_per_reservation"]
    min_lead = values["min_booking_lead_minutes"]
    max_lead_days = values["max_booking_lead_days"]

    if max_duration < min_duration:
        raise UnprocessableError(
            "reservation_max_duration_minutes não pode ser menor que o mínimo."
        )
    if not (min_duration <= step <= max_duration):
        raise UnprocessableError(
            "reservation_duration_step_minutes deve estar entre o mínimo e o máximo."
        )
    if max_people < min_people:
        raise UnprocessableError(
            "max_people_per_reservation não pode ser menor que o mínimo."
        )
    if min_lead >= max_lead_days * 24 * 60:
        raise UnprocessableError(
            "A antecedência mínima deve ser menor que a antecedência máxima."
        )


def update_settings(
    db: Session, restaurant_id: UUID, *, changes: dict
) -> RestaurantSettings:
    """Atualiza `RestaurantSettings` a partir de nomes públicos (parcial)."""
    settings = get_settings_or_404(db, restaurant_id)

    merged = {
        column: getattr(settings, column)
        for column in _SETTINGS_PUBLIC_TO_DOMAIN.values()
    }
    for public_field, value in changes.items():
        merged[_SETTINGS_PUBLIC_TO_DOMAIN[public_field]] = value

    _validate_settings_consistency(merged)

    for column, value in merged.items():
        setattr(settings, column, value)
    db.commit()
    db.refresh(settings)
    return settings


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------
def list_tables(
    db: Session, restaurant_id: UUID, *, include_locked: bool
) -> list[Table]:
    get_restaurant_or_404(db, restaurant_id)
    return repository.list_tables(db, restaurant_id, include_locked=include_locked)


def create_table(
    db: Session,
    *,
    restaurant_id: UUID,
    label: str,
    capacity: int,
    position_x: float | None,
    position_y: float | None,
    position_z: float | None,
    is_locked: bool,
) -> Table:
    get_restaurant_or_404(db, restaurant_id)
    if repository.get_table_by_label(db, restaurant_id, label) is not None:
        raise ConflictError("Table label already in use for this restaurant")

    table = Table(
        restaurant_id=restaurant_id,
        label=label.strip(),
        capacity=capacity,
        is_locked=is_locked,
        position_x=position_x,
        position_y=position_y,
        position_z=position_z,
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def update_table(db: Session, table_id: UUID, *, changes: dict) -> Table:
    table = repository.get_table(db, table_id)
    if table is None:
        raise NotFoundError("Table not found")

    if "label" in changes and changes["label"]:
        existing = repository.get_table_by_label(
            db, table.restaurant_id, changes["label"]
        )
        if existing is not None and existing.id != table.id:
            raise ConflictError("Table label already in use for this restaurant")
        changes["label"] = changes["label"].strip()

    for field, value in changes.items():
        setattr(table, field, value)
    db.commit()
    db.refresh(table)
    return table


# ---------------------------------------------------------------------------
# CapacityRule
# ---------------------------------------------------------------------------
def list_capacity_rules(
    db: Session, restaurant_id: UUID, *, include_inactive: bool
) -> list[CapacityRule]:
    get_restaurant_or_404(db, restaurant_id)
    return repository.list_capacity_rules(
        db, restaurant_id, include_inactive=include_inactive
    )


def _ensure_capacity_range(
    db: Session,
    *,
    restaurant_id: UUID,
    min_people: int,
    max_people: int,
    is_active: bool,
    exclude_rule_id: UUID | None = None,
) -> None:
    """Rejeita faixas inválidas ou sobrepostas a outra regra ativa (DOMAIN_SPEC §2.5)."""
    if max_people < min_people:
        raise UnprocessableError("max_people deve ser maior ou igual a min_people")
    if not is_active:
        return
    for rule in repository.list_active_capacity_rules(db, restaurant_id):
        if exclude_rule_id is not None and rule.id == exclude_rule_id:
            continue
        if _ranges_overlap(min_people, max_people, rule.min_people, rule.max_people):
            raise UnprocessableError(
                "Faixa de capacidade sobreposta a uma regra existente "
                f"({rule.min_people}–{rule.max_people})."
            )


def create_capacity_rule(
    db: Session,
    *,
    restaurant_id: UUID,
    min_people: int,
    max_people: int,
    tables_required: int,
    is_active: bool,
) -> CapacityRule:
    # Bloqueia a linha do restaurante para serializar a validação anti-sobreposição.
    if repository.lock_restaurant(db, restaurant_id) is None:
        raise NotFoundError("Restaurant not found")
    _ensure_capacity_range(
        db,
        restaurant_id=restaurant_id,
        min_people=min_people,
        max_people=max_people,
        is_active=is_active,
    )
    rule = CapacityRule(
        restaurant_id=restaurant_id,
        min_people=min_people,
        max_people=max_people,
        tables_required=tables_required,
        is_active=is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_capacity_rule(db: Session, rule_id: UUID, *, changes: dict) -> CapacityRule:
    rule = repository.get_capacity_rule(db, rule_id)
    if rule is None:
        raise NotFoundError("Capacity rule not found")
    if repository.lock_restaurant(db, rule.restaurant_id) is None:
        raise NotFoundError("Restaurant not found")

    min_people = changes.get("min_people", rule.min_people)
    max_people = changes.get("max_people", rule.max_people)
    is_active = changes.get("is_active", rule.is_active)
    _ensure_capacity_range(
        db,
        restaurant_id=rule.restaurant_id,
        min_people=min_people,
        max_people=max_people,
        is_active=is_active,
        exclude_rule_id=rule.id,
    )
    for field, value in changes.items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule
