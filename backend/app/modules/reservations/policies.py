"""Políticas de reserva — funções puras (sem banco).

Concentram as regras que antes poderiam ficar espalhadas: duração (ADR-010),
antecedência (ADR-010), janela de cancelamento (R14/ADR-010), overlap de intervalos
(ADR-011 — intervalo `[start, end)`) e transições de status (DOMAIN_SPEC §4.2).

São independentes de persistência para serem testáveis unitariamente e para que
`ReservationService`/availability reutilizem a **mesma** implementação.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from app.core.exceptions import ConflictError, UnprocessableError
from app.modules.reservations.model import ReservationStatus

# Transições documentadas (docs/DOMAIN_SPEC.md §4.2). Estados terminais não transicionam.
_ALLOWED_TRANSITIONS: dict[ReservationStatus, frozenset[ReservationStatus]] = {
    ReservationStatus.PENDING: frozenset(
        {ReservationStatus.CONFIRMED, ReservationStatus.CANCELLED}
    ),
    ReservationStatus.CONFIRMED: frozenset(
        {
            ReservationStatus.COMPLETED,
            ReservationStatus.NO_SHOW,
            ReservationStatus.CANCELLED,
        }
    ),
    ReservationStatus.COMPLETED: frozenset(),
    ReservationStatus.NO_SHOW: frozenset(),
    ReservationStatus.CANCELLED: frozenset(),
}

# Status que ainda podem ser editados/cancelados pelo fluxo negocial.
EDITABLE_STATUSES = frozenset(
    {ReservationStatus.PENDING, ReservationStatus.CONFIRMED}
)
CANCELLABLE_STATUSES = frozenset(
    {ReservationStatus.PENDING, ReservationStatus.CONFIRMED}
)


def combine_start_at(reservation_date: date, start_time: time) -> datetime:
    """Combina `date` + `start_time` em um datetime **aware** (UTC).

    O domínio não define timezone do restaurante (D10 aberto): até que isso seja
    decidido, o horário de parede informado é tratado como UTC. Nunca se compara
    datetime *aware* com *naive*.
    """
    return datetime.combine(reservation_date, start_time, tzinfo=timezone.utc)


def reservation_interval(
    reservation_date: date, start_time: time, duration_minutes: int
) -> tuple[datetime, datetime]:
    """Intervalo `[start, end)` da reserva (ADR-011)."""
    start = combine_start_at(reservation_date, start_time)
    return start, start + timedelta(minutes=duration_minutes)


def intervals_overlap(
    start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime
) -> bool:
    """Sobreposição de intervalos meio-abertos `[start, end)` (ADR-011).

    `19–21` e `21–23` **não** sobrepõem; `19–21` e `20–22` sobrepõem.
    """
    return start_a < end_b and start_b < end_a


def is_duration_allowed(
    duration_minutes: int, *, minimum: int, maximum: int, step: int
) -> bool:
    """Duração permitida: dentro de `[minimum, maximum]` e múltipla do passo (ADR-010).

    O passo é lido da configuração do restaurante e medido a partir de zero
    (API_SPEC §7: "múltiplo do passo"). Com os defaults (30–180, passo 30):
    30/60/90/120/150/180 válidos; 45/75 inválidos.
    """
    if duration_minutes < minimum or duration_minutes > maximum:
        return False
    if step <= 0:
        return True
    return duration_minutes % step == 0


def ensure_duration_allowed(
    duration_minutes: int, *, minimum: int, maximum: int, step: int
) -> None:
    if not is_duration_allowed(
        duration_minutes, minimum=minimum, maximum=maximum, step=step
    ):
        raise UnprocessableError(
            f"duration_minutes={duration_minutes} fora dos limites configurados "
            f"(min={minimum}, max={maximum}, step={step})"
        )


def ensure_people_count_allowed(people_count: int, *, minimum: int, maximum: int) -> None:
    if people_count < minimum or people_count > maximum:
        raise UnprocessableError(
            f"people_count={people_count} fora dos limites configurados "
            f"(min={minimum}, max={maximum})"
        )


def ensure_lead_time(
    start_at: datetime,
    *,
    now: datetime,
    min_lead_minutes: int,
    max_lead_days: int,
) -> None:
    """Antecedência mínima/máxima (ADR-010).

    `now + min_lead_minutes <= start_at <= now + max_lead_days`.
    Exemplos (min 60, max 90 dias): 59 min → rejeita; 60 min → aceita;
    exatamente 90 dias → aceita; 90 dias + 1 min → rejeita.
    """
    earliest = now + timedelta(minutes=min_lead_minutes)
    latest = now + timedelta(days=max_lead_days)
    if start_at < earliest:
        raise UnprocessableError(
            "A antecedência mínima para reservar é de "
            f"{min_lead_minutes} minutos a partir de agora."
        )
    if start_at > latest:
        raise UnprocessableError(
            f"A antecedência máxima para reservar é de {max_lead_days} dias."
        )


def can_cancel(
    start_at: datetime, *, now: datetime, cancellation_window_minutes: int
) -> bool:
    """Cancelamento permitido até `cancellation_window_minutes` antes do início (R14)."""
    return now <= start_at - timedelta(minutes=cancellation_window_minutes)


def can_transition(
    current: ReservationStatus, target: ReservationStatus
) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def ensure_transition(
    current: ReservationStatus, target: ReservationStatus
) -> None:
    """Rejeita transições não documentadas (DOMAIN_SPEC §4.2) com `409 Conflict`."""
    if not can_transition(current, target):
        raise ConflictError(
            f"Transição de status inválida: {current.value} → {target.value}"
        )
