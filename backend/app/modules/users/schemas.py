"""Schemas públicos (DTOs) do módulo `users`.

Separação conceitual (request / response / domínio): este arquivo expõe apenas
response schemas; a entidade ORM (`User`) nunca é exposta diretamente pela API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.users.model import UserRole


class UserRead(BaseModel):
    """Representação pública de um usuário (nunca inclui password_hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
