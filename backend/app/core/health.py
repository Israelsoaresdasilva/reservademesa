"""Health check da API e da conexão com o banco.

`GET /health`      — a API está no ar (independe de banco).
`GET /health/db`   — verifica a conexão PostgreSQL (SELECT 1). 503 se indisponível.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.database import database_is_reachable

router = APIRouter(tags=["system"])


@router.get("/health", summary="Health check da API")
def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db", summary="Health check da conexão com o banco")
def health_db():
    if database_is_reachable():
        return {"status": "ok"}
    return JSONResponse(
        status_code=503,
        content={"status": "unavailable", "detail": "Database unavailable"},
    )
