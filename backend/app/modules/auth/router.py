"""Router do módulo `auth`.

Foundation da Fase 2 — endpoints seguem os contratos de docs/API_SPEC.md §4.
Camada de transporte apenas: valida schema, chama service, serializa resposta.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, LoginResponse, MeResponse, RegisterRequest, RegisterResponse
from app.modules.users.model import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Cadastro de cliente",
    description="Fase 2 (foundation). Cria conta CUSTOMER e devolve sessão (docs/API_SPEC.md §4).",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    user = service.register_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        phone=payload.phone,
    )
    return RegisterResponse(user=UserRead.model_validate(user), token=service.issue_access_token(user))


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Fase 2 (foundation). Access token sem refresh (ADR-014); contrato em docs/API_SPEC.md §4.",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = service.authenticate_user(db, email=payload.email, password=payload.password)
    return LoginResponse(
        access_token=service.issue_access_token(user),
        user=UserRead.model_validate(user),
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Perfil da sessão",
    description="Usuário autenticado (CUSTOMER | ADMIN). Também valida a sessão.",
)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(user=UserRead.model_validate(current_user))
