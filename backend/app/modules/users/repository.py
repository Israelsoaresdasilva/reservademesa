"""Repository do módulo `users` — fronteira de acesso a dados.

Camada conforme docs/ARCHITECTURE.md §4 (repository). Regras de negócio
permanecem nos services.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.users.model import User, UserRole


def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(func.lower(User.email) == email.strip().lower())
    return db.scalar(stmt)


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    phone: str | None = None,
    role: UserRole = UserRole.CUSTOMER,
) -> User:
    """Cria e faz flush do usuário (persistência efetiva via commit no service)."""
    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        phone=phone.strip() if phone else None,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.flush()
    return user
