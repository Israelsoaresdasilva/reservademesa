"""Testes de integração — reservas end-to-end (exigem PostgreSQL real).

Cobrem criação/alteração/cancelamento, alocação por `CapacityRule`, mesas bloqueadas,
overlap (ADR-011), rollback transacional, constraint `UNIQUE(reservation_id, table_id)`,
autorização por proprietário e **concorrência** (double booking). Sem banco → auto-skip.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.modules.reservations.model import ReservationTable


def _future_date(days: int = 10) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()


def _setup_restaurant(
    client, admin_headers, restaurant_factory, *, tables, capacity_rules
) -> str:
    restaurant_id = restaurant_factory()["id"]
    for table in tables:
        response = client.post(
            "/tables",
            json={"restaurant_id": restaurant_id, **table},
            headers=admin_headers,
        )
        assert response.status_code == 201, response.text
    for rule in capacity_rules:
        response = client.post(
            "/admin/capacity-rules",
            json={"restaurant_id": restaurant_id, **rule},
            headers=admin_headers,
        )
        assert response.status_code == 201, response.text
    return restaurant_id


FULL_RANGE = {"min_people": 1, "max_people": 4, "tables_required": 1}


@pytest.mark.integration
def test_create_get_update_cancel_flow(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    reservation_date = _future_date()

    created = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": reservation_date,
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    reservation = body["reservation"]
    reservation_id = reservation["id"]
    assert reservation["status"] == "PENDING"
    assert reservation["start_time"] == "19:00"
    assert reservation["date"] == reservation_date
    assert len(body["allocated_tables"]) == 1
    assert body["allocated_tables"][0]["label"] == "1"

    detail = client.get(f"/reservations/{reservation_id}", headers=customer_headers)
    assert detail.status_code == 200
    assert detail.json()["id"] == reservation_id

    listing = client.get("/reservations", headers=customer_headers)
    assert listing.status_code == 200
    assert any(item["id"] == reservation_id for item in listing.json()["items"])

    updated = client.patch(
        f"/reservations/{reservation_id}",
        json={"people_count": 4, "start_time": "21:00", "notes": "Mesa na janela"},
        headers=customer_headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["people_count"] == 4
    assert updated.json()["start_time"] == "21:00"
    assert updated.json()["notes"] == "Mesa na janela"

    cancelled = client.delete(
        f"/reservations/{reservation_id}", headers=customer_headers
    )
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "CANCELLED"
    assert cancelled.json()["cancelled_by"] == "CUSTOMER"
    assert cancelled.json()["cancelled_at"] is not None
    # As mesas permanecem como histórico (sem exclusão física).
    assert len(cancelled.json()["allocated_tables"]) == 1

    again = client.delete(f"/reservations/{reservation_id}", headers=customer_headers)
    assert again.status_code == 409


@pytest.mark.integration
def test_locked_table_is_never_allocated(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[
            {"label": "1", "capacity": 4, "is_locked": True},
            {"label": "2", "capacity": 4},
        ],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    created = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert created.status_code == 201, created.text
    assert {t["label"] for t in created.json()["allocated_tables"]} == {"2"}


@pytest.mark.integration
def test_fully_locked_room_returns_409(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4, "is_locked": True}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    response = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert response.status_code == 409


@pytest.mark.integration
def test_missing_capacity_rule_returns_422(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[],
    )
    customer_headers, _ = customer_factory()
    response = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_invalid_duration_and_lead_time_return_422(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    base = {
        "restaurant_id": restaurant_id,
        "date": _future_date(),
        "start_time": "19:00",
        "people_count": 2,
    }

    # Duração fora do passo (45) e fora do máximo (210).
    for duration in (45, 210):
        response = client.post(
            "/reservations",
            json={**base, "duration_minutes": duration},
            headers=customer_headers,
        )
        assert response.status_code == 422, duration

    # Antecedência mínima (< 60 min): hoje, ~30 min à frente.
    soon = datetime.now(timezone.utc) + timedelta(minutes=30)
    too_soon = {
        "restaurant_id": restaurant_id,
        "date": soon.date().isoformat(),
        "start_time": soon.strftime("%H:%M"),
        "duration_minutes": 120,
        "people_count": 2,
    }
    assert (
        client.post("/reservations", json=too_soon, headers=customer_headers).status_code
        == 422
    )

    # Antecedência máxima (> 90 dias).
    too_far = {**base, "date": _future_date(91), "duration_minutes": 120}
    assert (
        client.post("/reservations", json=too_far, headers=customer_headers).status_code
        == 422
    )


@pytest.mark.integration
def test_overlap_conflict_and_adjacent_allowed(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    first_customer, _ = customer_factory()
    second_customer, _ = customer_factory()
    base = {
        "restaurant_id": restaurant_id,
        "date": _future_date(),
        "duration_minutes": 120,
        "people_count": 2,
    }

    first = client.post(
        "/reservations",
        json={**base, "start_time": "19:00"},
        headers=first_customer,
    )
    assert first.status_code == 201, first.text

    # 20–22 sobrepõe 19–21 na mesma mesa → 409 (ADR-011).
    conflicting = client.post(
        "/reservations",
        json={**base, "start_time": "20:00"},
        headers=second_customer,
    )
    assert conflicting.status_code == 409

    # 21–23 é adjacente (limite `[start, end)`) → permitido.
    adjacent = client.post(
        "/reservations",
        json={**base, "start_time": "21:00"},
        headers=second_customer,
    )
    assert adjacent.status_code == 201, adjacent.text


@pytest.mark.integration
def test_capacity_rule_allocates_multiple_tables(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}, {"label": "2", "capacity": 4}],
        capacity_rules=[{"min_people": 5, "max_people": 8, "tables_required": 2}],
    )
    customer_headers, _ = customer_factory()
    created = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 6,
        },
        headers=customer_headers,
    )
    assert created.status_code == 201, created.text
    assert len(created.json()["allocated_tables"]) == 2


@pytest.mark.integration
def test_insufficient_tables_for_capacity_returns_409(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[{"min_people": 5, "max_people": 8, "tables_required": 2}],
    )
    customer_headers, _ = customer_factory()
    response = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 6,
        },
        headers=customer_headers,
    )
    assert response.status_code == 409


@pytest.mark.integration
def test_availability_reflects_allocation(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    params = {
        "restaurant_id": restaurant_id,
        "date": _future_date(),
        "start_time": "19:00",
        "duration_minutes": 120,
        "people_count": 2,
    }

    before = client.get(
        "/reservations/availability", params=params, headers=customer_headers
    )
    assert before.status_code == 200, before.text
    assert before.json()["status"] == "available"
    assert before.json()["estimated_tables"] == 1
    assert before.json()["conflicting_slots"] == []

    assert (
        client.post("/reservations", json=params, headers=customer_headers).status_code
        == 201
    )

    after = client.get(
        "/reservations/availability", params=params, headers=customer_headers
    )
    assert after.json()["status"] == "unavailable"


@pytest.mark.integration
def test_failed_creation_rolls_back(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    # Sala sem mesas elegíveis → 409; nada deve ser persistido (rollback transacional).
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4, "is_locked": True}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    before = client.get("/reservations", headers=customer_headers).json()["total"]

    failed = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert failed.status_code == 409

    after = client.get("/reservations", headers=customer_headers).json()["total"]
    assert after == before


@pytest.mark.integration
def test_duplicate_reservation_table_is_rejected(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    created = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    reservation_id = UUID(body["reservation"]["id"])
    table_id = UUID(body["allocated_tables"][0]["id"])

    # UNIQUE(reservation_id, table_id) é garantia de integridade no banco.
    with SessionLocal() as db:
        db.add(
            ReservationTable(
                reservation_id=reservation_id,
                table_id=table_id,
                allocated_at=datetime.now(timezone.utc),
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


@pytest.mark.integration
def test_customer_cannot_access_another_customer_reservation(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    owner_headers, _ = customer_factory()
    other_headers, _ = customer_factory()
    created = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=owner_headers,
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["reservation"]["id"]

    assert (
        client.get(f"/reservations/{reservation_id}", headers=other_headers).status_code
        == 403
    )
    assert (
        client.patch(
            f"/reservations/{reservation_id}",
            json={"people_count": 3},
            headers=other_headers,
        ).status_code
        == 403
    )
    assert (
        client.delete(f"/reservations/{reservation_id}", headers=other_headers).status_code
        == 403
    )
    listing = client.get("/reservations", headers=other_headers).json()
    assert all(item["id"] != reservation_id for item in listing["items"])


@pytest.mark.integration
def test_concurrent_double_booking_leaves_single_winner(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    """Duas requisições simultâneas disputando a única mesa: só uma consegue (ADR-011)."""
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    first_customer, _ = customer_factory()
    second_customer, _ = customer_factory()
    payload = {
        "restaurant_id": restaurant_id,
        "date": _future_date(),
        "start_time": "19:00",
        "duration_minutes": 120,
        "people_count": 2,
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                client.post, "/reservations", json=payload, headers=headers
            )
            for headers in (first_customer, second_customer)
        ]
        results = [future.result() for future in futures]

    assert sorted(result.status_code for result in results) == [201, 409]

    admin_list = client.get(
        "/admin/reservations",
        params={"restaurant_id": restaurant_id},
        headers=admin_headers,
    )
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] == 1


@pytest.mark.integration
def test_admin_status_transitions(
    client, migrated_db, admin_headers, restaurant_factory, customer_factory
):
    restaurant_id = _setup_restaurant(
        client,
        admin_headers,
        restaurant_factory,
        tables=[{"label": "1", "capacity": 4}],
        capacity_rules=[FULL_RANGE],
    )
    customer_headers, _ = customer_factory()
    created = client.post(
        "/reservations",
        json={
            "restaurant_id": restaurant_id,
            "date": _future_date(),
            "start_time": "19:00",
            "duration_minutes": 120,
            "people_count": 2,
        },
        headers=customer_headers,
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["reservation"]["id"]

    confirmed = client.patch(
        f"/admin/reservations/{reservation_id}/status",
        json={"status": "CONFIRMED"},
        headers=admin_headers,
    )
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["status"] == "CONFIRMED"

    # CONFIRMED → PENDING não é transição documentada (DOMAIN_SPEC §4.2).
    invalid = client.patch(
        f"/admin/reservations/{reservation_id}/status",
        json={"status": "PENDING"},
        headers=admin_headers,
    )
    assert invalid.status_code == 409

    completed = client.patch(
        f"/admin/reservations/{reservation_id}/status",
        json={"status": "COMPLETED"},
        headers=admin_headers,
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"

    admin_list = client.get(
        "/admin/reservations",
        params={"restaurant_id": restaurant_id},
        headers=admin_headers,
    )
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] >= 1

    # CUSTOMER não acessa a listagem administrativa.
    assert (
        client.get("/admin/reservations", headers=customer_headers).status_code == 403
    )
