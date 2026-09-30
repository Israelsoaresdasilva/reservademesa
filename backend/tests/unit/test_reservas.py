"""Testes unitários do módulo `reservas` (sem banco).

Cobrem a normalização de CPF/nome e a validação de campos — a regra de
unicidade CPF+data (banco) é coberta pelos testes de integração.
"""

import pytest

from app.modules.reservas import service
from app.modules.reservas.service import (
    ReservaValidationError,
    normalize_cpf,
    normalize_nome,
    validate_reserva_fields,
)


def test_normalize_cpf_remove_mascara():
    assert normalize_cpf("123.456.789-00") == "12345678900"
    assert normalize_cpf("12345678900") == "12345678900"
    assert normalize_cpf("  123.456.789-00 ") == "12345678900"
    assert normalize_cpf("") == ""


def test_normalize_nome_colapsa_espacos():
    assert normalize_nome("  João   Silva  ") == "João Silva"
    assert normalize_nome("Maria") == "Maria"
    assert normalize_nome("") == ""


def test_validar_campos_ok():
    result = validate_reserva_fields(
        nome=" João  Silva ",
        cpf="123.456.789-00",
        telefone="21999999999",
        numero_pessoas=4,
        mesa="12",
    )
    assert result["nome"] == "João Silva"
    assert result["cpf"] == "12345678900"


def test_validar_cpf_curto_invalido():
    with pytest.raises(ReservaValidationError):
        validate_reserva_fields(
            nome="João", cpf="123", telefone="21999999999", numero_pessoas=4, mesa="12"
        )


def test_validar_nome_vazio_invalido():
    with pytest.raises(ReservaValidationError):
        validate_reserva_fields(
            nome="   ", cpf="12345678900", telefone="21999999999", numero_pessoas=4, mesa="12"
        )


def test_validar_numero_pessoas_invalido():
    with pytest.raises(ReservaValidationError):
        validate_reserva_fields(
            nome="João", cpf="12345678900", telefone="21999999999", numero_pessoas=0, mesa="12"
        )


def test_erros_carregam_status_http():
    assert ReservaValidationError().status_code == 400
    assert service.ReservaConflictError("x").status_code == 409
    assert service.ReservaNotFoundError().status_code == 404
