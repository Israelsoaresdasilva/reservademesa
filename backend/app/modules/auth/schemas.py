"""Schemas do módulo `auth` (contratos públicos da API).

Separação conceitual: `*Request` (entrada), `*Response` (saída).
Contratos conforme docs/API_SPEC.md §4.
"""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserRead


class RegisterRequest(BaseModel):
    """POST /auth/register — cria conta de cliente (role CUSTOMER)."""

    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=1, description="Senha (política de senha: [TBD] no produto)")
    phone: str | None = Field(default=None, max_length=32)


class RegisterResponse(BaseModel):
    """201 — conta criada com sessão (token)."""

    user: UserRead
    token: str


class LoginRequest(BaseModel):
    """POST /auth/login — autentica por e-mail + senha."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """200 — sessão autenticada (access token sem refresh — ADR-014)."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserRead


class MeResponse(BaseModel):
    """200 — perfil da sessão atual."""

    user: UserRead
