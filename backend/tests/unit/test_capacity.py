"""Testes unitários de resolução de capacidade e alocação de mesas (sem banco).

Cobre a regra `people_count → tables_required` (ADR-005), a ausência de regra (422),
mesas ocupadas/bloqueadas e a insuficiência de mesas (409).
"""

from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError, UnprocessableError
from app.modules.reservations import capacity


class FakeRule:
    def __init__(self, min_people, max_people, tables_required, is_active=True):
        self.min_people = min_people
        self.max_people = max_people
        self.tables_required = tables_required
        self.is_active = is_active


class FakeTable:
    def __init__(self):
        self.id = uuid4()


def _rules():
    # Faixas de exemplo do enunciado (valores reais vêm do banco).
    return [
        FakeRule(1, 2, 1),
        FakeRule(3, 4, 1),
        FakeRule(5, 8, 2),
    ]


@pytest.mark.parametrize(
    "people,expected",
    [(1, 1), (2, 1), (3, 1), (4, 1), (5, 2), (6, 2), (8, 2)],
)
def test_resolve_tables_required_by_range(people, expected):
    assert capacity.resolve_tables_required(people, _rules()) == expected


def test_no_applicable_rule_raises_422():
    with pytest.raises(UnprocessableError) as exc:
        capacity.resolve_tables_required(9, _rules())
    assert exc.value.status_code == 422


def test_inactive_rules_are_ignored():
    rules = [FakeRule(1, 4, 1, is_active=False), FakeRule(5, 8, 2)]
    with pytest.raises(UnprocessableError):
        capacity.resolve_tables_required(2, rules)
    assert capacity.resolve_tables_required(6, rules) == 2


def test_overlapping_rules_raise_conflict():
    rules = [FakeRule(1, 4, 1), FakeRule(2, 6, 2)]
    with pytest.raises(ConflictError) as exc:
        capacity.resolve_tables_required(3, rules)
    assert exc.value.status_code == 409


def test_available_tables_excludes_occupied():
    table_a, table_b = FakeTable(), FakeTable()
    free = capacity.available_tables([table_a, table_b], {table_b.id})
    assert free == [table_a]


def test_select_tables_skips_occupied():
    table_a, table_b, table_c = FakeTable(), FakeTable(), FakeTable()
    selected = capacity.select_tables([table_a, table_b, table_c], {table_a.id}, 1)
    assert selected == [table_b]


def test_select_tables_insufficient_raises_conflict():
    only_table = FakeTable()
    with pytest.raises(ConflictError) as exc:
        capacity.select_tables([only_table], {only_table.id}, 1)
    assert exc.value.status_code == 409


def test_select_tables_takes_exact_count():
    tables = [FakeTable() for _ in range(3)]
    selected = capacity.select_tables(tables, set(), 2)
    assert len(selected) == 2
