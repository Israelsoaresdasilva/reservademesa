"""Resolução de capacidade e seleção de mesas — funções puras (sem banco).

Fluxo (docs/DOMAIN_SPEC.md §5.2 — ADR-005):

    people_count → CapacityRule (faixa → nº de mesas) → mesas necessárias
                 → mesas elegíveis e livres → alocação

Os valores das faixas **não** são fixos: vêm das `CapacityRule` do restaurante.
Sem regra aplicável → `422` (sem fallback silencioso). Sem mesas suficientes → `409`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol
from uuid import UUID

from app.core.exceptions import ConflictError, UnprocessableError


class _CapacityRuleLike(Protocol):
    """Contrato mínimo de uma regra de capacidade (evita dependência do ORM aqui)."""

    min_people: int
    max_people: int
    tables_required: int
    is_active: bool


class _TableLike(Protocol):
    id: UUID


def resolve_tables_required(
    people_count: int, rules: Iterable[_CapacityRuleLike]
) -> int:
    """Nº de mesas exigido para `people_count` segundo as regras ativas.

    - nenhuma regra cobre o valor → `422` (não há fallback silencioso);
    - mais de uma regra cobre o valor → `409` (faixas sobrepostas, integridade).
    """
    applicable = [
        rule
        for rule in rules
        if getattr(rule, "is_active", True)
        and rule.min_people <= people_count <= rule.max_people
    ]
    if not applicable:
        raise UnprocessableError(
            f"Nenhuma regra de capacidade cobre {people_count} pessoa(s)."
        )
    if len(applicable) > 1:
        raise ConflictError(
            "Configuração de capacidade ambígua: faixas sobrepostas cobrem "
            f"{people_count} pessoa(s)."
        )
    return applicable[0].tables_required


def available_tables(
    candidates: Sequence[_TableLike], occupied_table_ids: set[UUID]
) -> list[_TableLike]:
    """Mesas elegíveis (já sem bloqueadas/inativas) que estão livres no intervalo."""
    return [table for table in candidates if table.id not in occupied_table_ids]


def select_tables(
    candidates: Sequence[_TableLike], occupied_table_ids: set[UUID], required: int
) -> list[_TableLike]:
    """Seleciona `required` mesas livres; insuficientes → `409 Conflict`."""
    free = available_tables(candidates, occupied_table_ids)
    if len(free) < required:
        raise ConflictError(
            "Não há mesas suficientes disponíveis para o horário solicitado."
        )
    return free[:required]
