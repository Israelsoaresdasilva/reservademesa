"""CLI administrativa do backend Blue.

Uso (a partir de `backend/`):

    python -m app.cli create-admin [--name NOME] [--email EMAIL] [--phone TELEFONE]

Bootstrap administrativo (ADR-016): cria o primeiro usuário `ADMIN`. É o **único**
caminho para criar um `ADMIN`:

- o endpoint público `POST /auth/register` cria exclusivamente `CUSTOMER`;
- não existe `POST /auth/register-admin`;
- um `CUSTOMER` não consegue escolher `ADMIN` no request (o schema público não expõe
  `role`).

Segurança:
- a senha é sempre solicitada de forma interativa e não ecoada (`getpass`), nunca por
  argumento de linha de comando — evita exposição em histórico do shell / lista de processos;
- nenhuma credencial é escrita em log; na saída aparecem apenas e-mail, id e role;
- requer execução administrativa/local/operacional (acesso ao `DATABASE_URL`).

Depende de uma camada de service (docs/ARCHITECTURE.md §4): a CLI não contém regras de
negócio, apenas coleta de dados e apresentação do resultado.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.database import SessionLocal
from app.core.exceptions import ConflictError
from app.modules.users import service as users_service

PROG = "python -m app.cli"


def build_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos da CLI (exposto para testes)."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="CLI administrativa do backend Blue (bootstrap de ADMIN — ADR-016).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_admin = subparsers.add_parser(
        "create-admin",
        help="Cria o primeiro usuário ADMIN (bootstrap administrativo).",
        description=(
            "Cria um usuário com role ADMIN. E-mail já registrado é recusado. "
            "A senha é solicitada de forma segura (getpass)."
        ),
    )
    create_admin.add_argument("--name", help="Nome visível do ADMIN (pergunta se omitido).")
    create_admin.add_argument("--email", help="E-mail de acesso (pergunta se omitido).")
    create_admin.add_argument("--phone", help="Telefone de contato (opcional).")
    create_admin.set_defaults(handler=_create_admin)

    return parser


def _prompt_non_empty(label: str) -> str:
    """Solicita um valor não vazio (repetindo enquanto a entrada for vazia)."""
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("Valor obrigatório.", file=sys.stderr)


def _prompt_email() -> str:
    """Solicita um e-mail validando minimamente o formato."""
    while True:
        email = _prompt_non_empty("E-mail do ADMIN")
        if "@" in email:
            return email
        print("Informe um e-mail válido.", file=sys.stderr)


def _prompt_password() -> str:
    """Solicita a senha com confirmação, sem ecoar no terminal (`getpass`)."""
    while True:
        password = getpass.getpass("Senha: ")
        if not password:
            print("A senha não pode ser vazia.", file=sys.stderr)
            continue
        confirm = getpass.getpass("Confirme a senha: ")
        if password != confirm:
            print("As senhas não conferem. Tente novamente.", file=sys.stderr)
            continue
        return password


def _create_admin(args: argparse.Namespace) -> int:
    """Handler de `create-admin`: coleta dados e delega ao service de `users`."""
    name = (args.name or _prompt_non_empty("Nome do ADMIN")).strip()
    email = (args.email or _prompt_email()).strip()
    phone = args.phone.strip() if args.phone else None
    # A senha nunca vem por argumento — sempre pela entrada segura.
    password = _prompt_password()

    with SessionLocal() as db:
        try:
            user = users_service.create_admin_user(
                db, name=name, email=email, password=password, phone=phone
            )
        except ConflictError as exc:
            db.rollback()
            print(f"Erro: {exc.detail}", file=sys.stderr)
            return 1
        except IntegrityError:
            db.rollback()
            print("Erro: e-mail já registrado.", file=sys.stderr)
            return 1
        except SQLAlchemyError as exc:
            db.rollback()
            print(
                f"Erro de banco ({exc.__class__.__name__}): verifique DATABASE_URL e se "
                "as migrations estão aplicadas (alembic upgrade head).",
                file=sys.stderr,
            )
            return 1

    # Nunca imprimir credenciais (apenas identificação do usuário criado).
    print(f"ADMIN criado: {user.email} (id={user.id}, role={user.role.value})")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entrypoint da CLI. Retorna o código de saída do processo."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
