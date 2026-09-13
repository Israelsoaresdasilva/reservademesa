"""Service do módulo `users` — casos de uso de identidade e administração.

Regras de negócio ficam aqui (docs/ARCHITECTURE.md §4), nunca nos routers nem na CLI.
A CLI administrativa (`app/cli.py`) é apenas uma camada de transporte: valida entrada
interativa e chama este service.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.modules.users import repository as users_repository
from app.modules.users.model import User, UserRole


def create_admin_user(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    phone: str | None = None,
) -> User:
    """Cria a conta do primeiro `ADMIN` — bootstrap administrativo (ADR-016).

    Regras:
    - e-mail duplicado → `ConflictError` (409), mesma semântica do cadastro público;
    - `role` é forçada a `ADMIN` (nunca escolhida pelo cliente — `role` não existe no
      request público de registro);
    - a senha é armazenada somente como hash, com o mesmo hashing do sistema (Argon2
      via `pwdlib` — ADR-015).

    Só é alcançável por execução administrativa/local/operacional (CLI
    `python -m app.cli create-admin`); não existe endpoint público que crie `ADMIN`.
    """
    if users_repository.get_by_email(db, email) is not None:
        raise ConflictError("Email already registered")

    user = users_repository.create_user(
        db,
        name=name,
        email=email,
        password=password,
        phone=phone,
        role=UserRole.ADMIN,
    )
    db.commit()
    db.refresh(user)
    return user
