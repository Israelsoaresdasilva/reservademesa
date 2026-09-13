"""Testes unitários das políticas de reserva (sem banco).

Cobre duração (ADR-010), antecedência (ADR-010), janela de cancelamento (R14/R12),
overlap de intervalos (ADR-011 — `[start, end)`) e transições de status (DOMAIN_SPEC §4.2).
"""

from datetime import date, datetime, time, timedelta, timezone

import pytest

from app.core.exceptions import ConflictError, UnprocessableError
from app.modules.reservations import policies
from app.modules.reservations.model import ReservationStatus

MIN, MAX, STEP = 30, 180, 30
NOW = datetime(2030, 6, 1, 18, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------- duração
@pytest.mark.parametrize("duration", [30, 60, 90, 120, 150, 180])
def test_valid_durations(duration):
    assert policies.is_duration_allowed(duration, minimum=MIN, maximum=MAX, step=STEP)


@pytest.mark.parametrize("duration", [0, 15, 45, 75, 181, 210])
def test_invalid_durations(duration):
    assert not policies.is_duration_allowed(
        duration, minimum=MIN, maximum=MAX, step=STEP
    )


def test_duration_rule_generalizes_from_configuration():
    # Outra configuração (min=45, step=15): 45/60/.../180 válidos; 50 e 195 inválidos.
    assert policies.is_duration_allowed(45, minimum=45, maximum=180, step=15)
    assert policies.is_duration_allowed(180, minimum=45, maximum=180, step=15)
    assert not policies.is_duration_allowed(50, minimum=45, maximum=180, step=15)
    assert not policies.is_duration_allowed(195, minimum=45, maximum=180, step=15)


def test_ensure_duration_raises_422():
    with pytest.raises(UnprocessableError) as exc:
        policies.ensure_duration_allowed(45, minimum=MIN, maximum=MAX, step=STEP)
    assert exc.value.status_code == 422


# ---------------------------------------------------------------------- antecedência
def test_lead_time_minimum_boundary():
    policies.ensure_lead_time(
        NOW + timedelta(minutes=60), now=NOW, min_lead_minutes=60, max_lead_days=90
    )
    with pytest.raises(UnprocessableError):
        policies.ensure_lead_time(
            NOW + timedelta(minutes=59), now=NOW, min_lead_minutes=60, max_lead_days=90
        )


def test_lead_time_maximum_boundary():
    policies.ensure_lead_time(
        NOW + timedelta(days=90), now=NOW, min_lead_minutes=60, max_lead_days=90
    )
    with pytest.raises(UnprocessableError):
        policies.ensure_lead_time(
            NOW + timedelta(days=90, minutes=1),
            now=NOW,
            min_lead_minutes=60,
            max_lead_days=90,
        )


def test_people_count_bounds():
    policies.ensure_people_count_allowed(4, minimum=1, maximum=20)
    with pytest.raises(UnprocessableError):
        policies.ensure_people_count_allowed(21, minimum=1, maximum=20)


# --------------------------------------------------------------------------- tempo
def test_combine_start_at_is_utc_aware():
    start = policies.combine_start_at(date(2030, 6, 1), time(19, 0))
    assert start.tzinfo is not None
    assert start.utcoffset() == timedelta(0)
    assert start == datetime(2030, 6, 1, 19, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------- overlap
def test_overlap_adjacent_is_allowed():
    # 19–21 e 21–23 na mesma mesa → PERMITIDO (ADR-011).
    start, end = policies.reservation_interval(date(2030, 6, 1), time(19, 0), 120)
    other_start, other_end = policies.reservation_interval(
        date(2030, 6, 1), time(21, 0), 120
    )
    assert not policies.intervals_overlap(start, end, other_start, other_end)


def test_overlap_conflict():
    # 19–21 e 20–22 na mesma mesa → CONFLITO.
    start, end = policies.reservation_interval(date(2030, 6, 1), time(19, 0), 120)
    other_start, other_end = policies.reservation_interval(
        date(2030, 6, 1), time(20, 0), 120
    )
    assert policies.intervals_overlap(start, end, other_start, other_end)


def test_overlap_fully_contained():
    outer = policies.reservation_interval(date(2030, 6, 1), time(18, 0), 240)
    inner = policies.reservation_interval(date(2030, 6, 1), time(20, 0), 60)
    assert policies.intervals_overlap(*outer, *inner)


def test_overlap_across_midnight():
    start, end = policies.reservation_interval(date(2030, 6, 1), time(23, 0), 180)
    assert end == datetime(2030, 6, 2, 2, 0, tzinfo=timezone.utc)
    late_start, late_end = policies.reservation_interval(
        date(2030, 6, 2), time(1, 0), 60
    )
    assert policies.intervals_overlap(start, end, late_start, late_end)


# --------------------------------------------------------------------- cancelamento
def test_cancellation_window():
    assert policies.can_cancel(
        NOW + timedelta(minutes=90), now=NOW, cancellation_window_minutes=60
    )
    assert not policies.can_cancel(
        NOW + timedelta(minutes=30), now=NOW, cancellation_window_minutes=60
    )
    # Exatamente 60 min antes → ainda permitido (limite inclusivo).
    assert policies.can_cancel(
        NOW + timedelta(minutes=60), now=NOW, cancellation_window_minutes=60
    )


# --------------------------------------------------------------------------- status
def test_documented_status_transitions():
    assert policies.can_transition(
        ReservationStatus.PENDING, ReservationStatus.CONFIRMED
    )
    assert policies.can_transition(
        ReservationStatus.PENDING, ReservationStatus.CANCELLED
    )
    assert policies.can_transition(
        ReservationStatus.CONFIRMED, ReservationStatus.COMPLETED
    )
    assert policies.can_transition(
        ReservationStatus.CONFIRMED, ReservationStatus.NO_SHOW
    )
    assert policies.can_transition(
        ReservationStatus.CONFIRMED, ReservationStatus.CANCELLED
    )


def test_forbidden_status_transitions():
    assert not policies.can_transition(
        ReservationStatus.CANCELLED, ReservationStatus.PENDING
    )
    assert not policies.can_transition(
        ReservationStatus.CANCELLED, ReservationStatus.CONFIRMED
    )
    assert not policies.can_transition(
        ReservationStatus.COMPLETED, ReservationStatus.CONFIRMED
    )
    assert not policies.can_transition(
        ReservationStatus.PENDING, ReservationStatus.COMPLETED
    )


def test_ensure_transition_raises_conflict():
    with pytest.raises(ConflictError) as exc:
        policies.ensure_transition(
            ReservationStatus.CANCELLED, ReservationStatus.PENDING
        )
    assert exc.value.status_code == 409
