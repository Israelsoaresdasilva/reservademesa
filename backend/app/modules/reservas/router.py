"""Router do módulo `reservas` — endpoints públicos (sem autenticação).

Contrato do roadmap da raiz (`roadmap.md` §10–§15):
- `POST /api/reservas`            → cria reserva (409 se CPF+data já existir)
- `GET  /api/reservas`            → lista (filtro opcional `?data=YYYY-MM-DD`), por horário
- `GET  /api/reservas/{id}`       → detalhe (404 se não existir)
- `PUT  /api/reservas/{id}`       → atualiza (parcial; revalida CPF+data e mesa+data)
- `DELETE /api/reservas/{id}`     → exclui (uso administrativo)

Formato de resposta: `{ "success": true|false, ... }` (sucesso) e
`{ "success": false, "message": "..." }` (erro), conforme o roadmap.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.reservas import service
from app.modules.reservas.schemas import ReservaCreate, ReservaRead, ReservaUpdate

router = APIRouter(prefix="/api/reservas", tags=["reservas"])


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"success": False, "message": message})


@router.post("", status_code=201, summary="Criar reserva (público)")
def create_reserva(payload: ReservaCreate, db: Session = Depends(get_db)):
    try:
        reserva = service.create_reserva(db, payload)
    except (service.ReservaConflictError, service.ReservaValidationError) as exc:
        return _error(exc.status_code, exc.message)
    return {
        "success": True,
        "message": "Reserva realizada com sucesso.",
        "reserva": ReservaRead.from_reserva(reserva),
    }


@router.get("", summary="Listar reservas")
def list_reservas(
    data: date | None = Query(default=None, description="Filtra por data (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    reservas = service.list_reservas(db, data=data)
    return {
        "success": True,
        "items": [ReservaRead.from_reserva(r) for r in reservas],
        "total": len(reservas),
    }


@router.get("/{reserva_id}", summary="Detalhe da reserva")
def get_reserva(reserva_id: UUID, db: Session = Depends(get_db)):
    try:
        reserva = service.get_reserva(db, reserva_id)
    except service.ReservaNotFoundError as exc:
        return _error(exc.status_code, exc.message)
    return {"success": True, "reserva": ReservaRead.from_reserva(reserva)}


@router.put("/{reserva_id}", summary="Atualizar reserva (parcial)")
def update_reserva(reserva_id: UUID, payload: ReservaUpdate, db: Session = Depends(get_db)):
    try:
        reserva = service.update_reserva(db, reserva_id, payload)
    except (
        service.ReservaConflictError,
        service.ReservaValidationError,
        service.ReservaNotFoundError,
    ) as exc:
        return _error(exc.status_code, exc.message)
    return {
        "success": True,
        "message": "Reserva atualizada com sucesso.",
        "reserva": ReservaRead.from_reserva(reserva),
    }


@router.delete("/{reserva_id}", summary="Excluir reserva")
def delete_reserva(reserva_id: UUID, db: Session = Depends(get_db)):
    try:
        service.delete_reserva(db, reserva_id)
    except service.ReservaNotFoundError as exc:
        return _error(exc.status_code, exc.message)
    return {"success": True, "message": "Reserva excluída com sucesso."}
