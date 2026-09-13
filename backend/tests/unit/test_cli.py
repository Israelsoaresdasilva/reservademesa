"""Testes unitários da CLI administrativa (sem banco).

Cobrem o parser de argumentos e a coleta segura de dados (senha via getpass,
e-mail validado). A criação efetiva de ADMIN exige PostgreSQL e é coberta em
`tests/integration/test_admin_bootstrap.py` (ADR-016).
"""

from unittest.mock import patch

import pytest

from app.cli import _prompt_email, _prompt_password, build_parser


def test_parser_requires_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_accepts_create_admin():
    parser = build_parser()
    args = parser.parse_args(
        ["create-admin", "--name", "Admin", "--email", "admin@example.com"]
    )
    assert args.command == "create-admin"
    assert args.name == "Admin"
    assert args.email == "admin@example.com"
    assert callable(args.handler)


def test_prompt_email_rejects_invalid_then_accepts():
    with patch("builtins.input", side_effect=["sem-arroba", "admin@example.com"]):
        assert _prompt_email() == "admin@example.com"


def test_prompt_password_retries_on_mismatch():
    # 1ª tentativa: confirmação diferente; 2ª tentativa: confere.
    with patch("app.cli.getpass.getpass", side_effect=["a", "b", "segredo", "segredo"]):
        assert _prompt_password() == "segredo"
