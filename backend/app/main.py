"""Blue backend — entrypoint da aplicação FastAPI.

Composição:
- routers de infraestrutura (`/health`) e da foundation (`/auth`);
- handlers de exceções de aplicação (docs/API_SPEC.md §2);
- OpenAPI automática em `/docs`.

Inicialização não conecta ao banco (conexão é lazy por request) — assim o servidor
sobe mesmo se o PostgreSQL estiver indisponível; `/health/db` reporta o estado.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.health import router as health_router
from app.modules.auth.router import router as auth_router
from app.modules.reservas.router import router as reservas_router
from app.modules.reservations.router import admin_router as reservations_admin_router
from app.modules.reservations.router import router as reservations_router
from app.modules.restaurants.router import admin_router as restaurants_admin_router
from app.modules.restaurants.router import router as restaurants_router
from app.modules.restaurants.router import tables_router

API_TITLE = "Blue API"
API_VERSION = "0.2.0"


def _configure_logging() -> None:
    logging.getLogger().setLevel(settings.LOG_LEVEL.upper())


def create_app() -> FastAPI:
    _configure_logging()

    application = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description=(
            "Blue v1 — backend foundation (Fase 2). "
            "Stack: Python/FastAPI/PostgreSQL/SQLAlchemy/Alembic/JWT. "
            "Ver docs/ em ../docs."
        ),
    )

    # CORS para o frontend de desenvolvimento (Vite). Origens configuráveis via env.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Endpoints de infraestrutura
    application.include_router(health_router)

    # Fluxo público de reserva simples (roadmap da raiz) — sem autenticação.
    application.include_router(reservas_router)

    # Módulos da foundation
    application.include_router(auth_router)

    # Fase 3 — restaurante e reservas (docs/API_SPEC.md §6/§7/§8/§14)
    application.include_router(restaurants_router)
    application.include_router(tables_router)
    application.include_router(restaurants_admin_router)
    application.include_router(reservations_router)
    application.include_router(reservations_admin_router)

    @application.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Normaliza erros de aplicação no formato {"detail": ...}."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return application


app = create_app()
