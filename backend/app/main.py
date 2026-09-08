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
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.health import router as health_router
from app.modules.auth.router import router as auth_router

API_TITLE = "Blue API"
API_VERSION = "0.1.0"


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

    # Endpoints de infraestrutura
    application.include_router(health_router)

    # Módulos da foundation
    application.include_router(auth_router)

    @application.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Normaliza erros de aplicação no formato {"detail": ...}."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return application


app = create_app()
