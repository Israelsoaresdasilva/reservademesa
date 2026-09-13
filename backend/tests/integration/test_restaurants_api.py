"""Testes de integração — restaurante, settings, mesas e CapacityRule (exigem PostgreSQL).

Exercitam ORM + migrations + camadas router→service→repository. Pulos automáticos sem banco.
"""

import uuid

import pytest


@pytest.mark.integration
def test_create_restaurant_with_default_settings(client, migrated_db, admin_headers):
    slug = f"ocean-{uuid.uuid4().hex[:10]}"
    response = client.post(
        "/restaurants",
        json={"name": "Ocean Blue", "slug": slug, "phone": "11999990000"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    restaurant = response.json()
    assert restaurant["slug"] == slug
    assert restaurant["is_active"] is True

    settings = client.get(
        f"/restaurants/{restaurant['id']}/settings", headers=admin_headers
    )
    assert settings.status_code == 200, settings.text
    body = settings.json()
    # Defaults do ADR-010.
    assert body["cancellation_window_minutes"] == 60
    assert body["min_booking_lead_minutes"] == 60
    assert body["max_booking_lead_days"] == 90
    assert body["min_duration_minutes"] == 30
    assert body["max_duration_minutes"] == 180
    assert body["duration_step_minutes"] == 30
    assert body["min_people"] == 1
    assert body["max_people"] == 20

    detail = client.get(f"/restaurants/{restaurant['id']}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["settings"]["duration_step_minutes"] == 30

    listing = client.get("/restaurants", headers=admin_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1


@pytest.mark.integration
def test_restaurant_creation_requires_admin(client, migrated_db, customer_factory):
    customer_headers, _ = customer_factory()
    response = client.post(
        "/restaurants", json={"name": "Nao permitido"}, headers=customer_headers
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_customer_only_sees_unlocked_tables(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant = restaurant_factory()
    restaurant_id = restaurant["id"]
    for payload in (
        {"restaurant_id": restaurant_id, "label": "1", "capacity": 2},
        {"restaurant_id": restaurant_id, "label": "2", "capacity": 4, "is_locked": True},
    ):
        assert (
            client.post("/tables", json=payload, headers=admin_headers).status_code
            == 201
        )

    customer_headers, _ = customer_factory()
    as_customer = client.get(
        f"/restaurants/{restaurant_id}/tables", headers=customer_headers
    )
    assert as_customer.status_code == 200
    assert {t["label"] for t in as_customer.json()["items"]} == {"1"}

    as_admin = client.get(
        f"/restaurants/{restaurant_id}/tables", headers=admin_headers
    )
    assert {t["label"] for t in as_admin.json()["items"]} == {"1", "2"}


@pytest.mark.integration
def test_duplicate_table_label_returns_409(
    client, migrated_db, admin_headers, restaurant_factory
):
    restaurant_id = restaurant_factory()["id"]
    payload = {"restaurant_id": restaurant_id, "label": "A", "capacity": 2}
    assert client.post("/tables", json=payload, headers=admin_headers).status_code == 201
    duplicate = client.post("/tables", json=payload, headers=admin_headers)
    assert duplicate.status_code == 409


@pytest.mark.integration
def test_capacity_rule_overlap_rejected_422(
    client, migrated_db, admin_headers, restaurant_factory
):
    restaurant_id = restaurant_factory()["id"]
    first = client.post(
        "/admin/capacity-rules",
        json={
            "restaurant_id": restaurant_id,
            "min_people": 1,
            "max_people": 4,
            "tables_required": 1,
        },
        headers=admin_headers,
    )
    assert first.status_code == 201, first.text

    overlapping = client.post(
        "/admin/capacity-rules",
        json={
            "restaurant_id": restaurant_id,
            "min_people": 4,
            "max_people": 8,
            "tables_required": 2,
        },
        headers=admin_headers,
    )
    assert overlapping.status_code == 422

    contiguous = client.post(
        "/admin/capacity-rules",
        json={
            "restaurant_id": restaurant_id,
            "min_people": 5,
            "max_people": 8,
            "tables_required": 2,
        },
        headers=admin_headers,
    )
    assert contiguous.status_code == 201, contiguous.text

    listing = client.get(
        "/admin/capacity-rules",
        params={"restaurant_id": restaurant_id},
        headers=admin_headers,
    )
    assert listing.status_code == 200
    assert len(listing.json()["items"]) == 2


@pytest.mark.integration
def test_admin_settings_update_validation(
    client, migrated_db, admin_headers, restaurant_factory
):
    restaurant_id = restaurant_factory()["id"]

    invalid = client.patch(
        f"/admin/restaurants/{restaurant_id}/settings",
        json={"min_duration_minutes": 120, "max_duration_minutes": 60},
        headers=admin_headers,
    )
    assert invalid.status_code == 422

    valid = client.patch(
        f"/admin/restaurants/{restaurant_id}/settings",
        json={"max_booking_lead_days": 30, "cancellation_window_minutes": 120},
        headers=admin_headers,
    )
    assert valid.status_code == 200, valid.text
    assert valid.json()["max_booking_lead_days"] == 30
    assert valid.json()["cancellation_window_minutes"] == 120
