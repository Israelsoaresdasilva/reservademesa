"""Service do módulo `auth` — casos de uso da fundação de autenticação.

Regras de negócio ficam aqui (docs/ARCHITECTURE.md §4), nunca nos routers.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.modules.users import repository as users_repository
from app.modules.users.model import User, UserRole


def register_user(db: Session, *, name: str, email: str, password: str, phone: str | None) -> User:
    """Cria conta de cliente (CUSTOMER). E-mail duplicado → 409 (docs/API_SPEC.md §4)."""
    if users_repository.get_by_email(db, email) is not None:
        raise ConflictError("Email already registered")

    user = users_repository.create_user(
        db,
        name=name,
        email=email,
        password=password,
        phone=phone,
        role=UserRole.CUSTOMER,
    )
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    """Autentica credenciais. Falha → 401 (sem revelar se o e-mail existe)."""
    user = users_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
    if not user.is_active:
        raise UnauthorizedError("Inactive account")
    return user


def issue_access_token(user: User) -> str:
    """Emite JWT access token (ADR-014) com o subject = id do usuário."""
    return create_access_token(subject=user.id, role=user.role.value)
