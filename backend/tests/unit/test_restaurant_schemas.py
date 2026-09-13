"""Testes unitários dos schemas de `restaurants` (mapeamento settings, sem banco).

O `GET /restaurants/{id}` expõe `settings` com nomes públicos (API_SPEC §6); o mapeamento
das colunas do domínio é feito por `RestaurantSettingsPublic.from_settings`.
"""

from datetime import datetime, timezone
from uuid import uuid4

from app.modules.restaurants.schemas import (
    RestaurantDetailRead,
    RestaurantRead,
    RestaurantSettingsPublic,
)


class _Settings:
    reservation_min_duration_minutes = 30
    reservation_max_duration_minutes = 180
    reservation_duration_step_minutes = 30
    min_people_per_reservation = 1
    max_people_per_reservation = 20
    cancellation_window_minutes = 60
    min_booking_lead_minutes = 60
    max_booking_lead_days = 90
    preorder_enabled = True


class _Restaurant:
    def __init__(self):
        self.id = uuid4()
        self.name = "Ocean Blue"
        self.slug = "ocean"
        self.phone = None
        self.description = None
        self.address = None
        self.is_active = True
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.settings = _Settings()


def test_settings_public_maps_domain_column_names():
    public = RestaurantSettingsPublic.from_settings(_Settings())
    assert public.min_duration_minutes == 30
    assert public.max_duration_minutes == 180
    assert public.duration_step_minutes == 30
    assert public.min_people == 1
    assert public.max_people == 20


def test_restaurant_detail_read_construction():
    restaurant = _Restaurant()
    base = RestaurantRead.model_validate(restaurant)
    detail = RestaurantDetailRead(
        **base.model_dump(),
        settings=RestaurantSettingsPublic.from_settings(restaurant.settings),
    )
    assert detail.name == "Ocean Blue"
    assert detail.settings is not None
    assert detail.settings.cancellation_window_minutes == 60


def test_restaurant_detail_read_without_settings():
    restaurant = _Restaurant()
    restaurant.settings = None
    base = RestaurantRead.model_validate(restaurant)
    detail = RestaurantDetailRead(**base.model_dump(), settings=None)
    assert detail.settings is None
