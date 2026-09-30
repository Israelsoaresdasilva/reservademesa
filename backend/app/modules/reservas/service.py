"""Service do módulo `reservas` — casos de uso e regra de negócio.

Regras (roadmap da raiz):
- CPF aceito com ou sem máscara, mas normalizado para 11 dígitos antes de salvar.
- Nome com espaços extras normalizados.
- **Um mesmo CPF não pode ter duas reservas na mesma data** (409). A unicidade é
  garantida no banco (`UNIQUE(cpf, data)`) e revalidada aqui antes de inserir.
"""

from __future__ import annotations

import re
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.reservas.model import Reserva
from app.modules.reservas.schemas import ReservaCreate, ReservaUpdate


class ReservaError(Exception):
    """Erro de domínio da reserva simples, com status HTTP e mensagem para o cliente."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class ReservaValidationError(ReservaError):
    """400 — dados da reserva inválidos."""

    def __init__(self, message: str = "Dados da reserva inválidos.") -> None:
        super().__init__(400, message)


class ReservaConflictError(ReservaError):
    """409 — CPF já possui reserva naquela data (regra de unicidade)."""

    def __init__(self, message: str) -> None:
        super().__init__(409, message)


class ReservaNotFoundError(ReservaError):
    """404 — reserva não encontrada."""

    def __init__(self, message: str = "Reserva não encontrada.") -> None:
        super().__init__(404, message)


def normalize_cpf(value: str) -> str:
    """Remove qualquer caractere não numérico do CPF (aceita com/sem máscara)."""
    return re.sub(r"\D", "", value or "")


def normalize_nome(value: str) -> str:
    """Remove espaços das pontas e colapsa espaços internos duplicados."""
    return re.sub(r"\s+", " ", (value or "").strip())


def validate_reserva_fields(
    *, nome: str, cpf: str, telefone: str, numero_pessoas: int, mesa: str
) -> dict:
    """Valida e normaliza os campos obrigatórios; retorna os valores normalizados."""
    nome_norm = normalize_nome(nome)
    cpf_norm = normalize_cpf(cpf)
    telefone_norm = (telefone or "").strip()
    mesa_norm = (mesa or "").strip()

    if not nome_norm:
        raise ReservaValidationError("Informe seu nome.")
    if len(cpf_norm) != 11:
        raise ReservaValidationError("CPF inválido. Deve conter 11 números.")
    if not telefone_norm:
        raise ReservaValidationError("Informe um telefone de contato.")
    if numero_pessoas < 1:
        raise ReservaValidationError("Informe o número de pessoas.")
    if not mesa_norm:
        raise ReservaValidationError("Selecione uma mesa.")

    return {"nome": nome_norm, "cpf": cpf_norm, "telefone": telefone_norm, "mesa": mesa_norm}


def create_reserva(db: Session, payload: ReservaCreate) -> Reserva:
    """Cria a reserva validando campos e as unicidades CPF+data e mesa+data."""
    data = validate_reserva_fields(
        nome=payload.nome,
        cpf=payload.cpf,
        telefone=payload.telefone,
        numero_pessoas=payload.numeroPessoas,
        mesa=payload.mesa,
    )

    if (
        db.scalar(
            select(Reserva).where(Reserva.cpf == data["cpf"], Reserva.data == payload.data)
        )
        is not None
    ):
        raise ReservaConflictError("Este CPF já possui uma reserva para esta data.")

    if (
        db.scalar(
            select(Reserva).where(Reserva.mesa == data["mesa"], Reserva.data == payload.data)
        )
        is not None
    ):
        raise ReservaConflictError("Esta mesa já está reservada para este dia.")

    reserva = Reserva(
        nome=data["nome"],
        cpf=data["cpf"],
        telefone=data["telefone"],
        numero_pessoas=payload.numeroPessoas,
        data=payload.data,
        horario=payload.horario,
        mesa=data["mesa"],
    )
    db.add(reserva)
    try:
        db.commit()
    except IntegrityError as exc:
        # Corrida: duas requisições simultâneas. Descobre qual constraint violou.
        db.rollback()
        detail = str(exc.orig).lower() if exc.orig else ""
        if "uq_reservas_cpf_data" in detail:
            raise ReservaConflictError("Este CPF já possui uma reserva para esta data.") from None
        raise ReservaConflictError("Esta mesa já está reservada para este dia.") from None
    db.refresh(reserva)
    return reserva


def update_reserva(db: Session, reserva_id: UUID, payload: ReservaUpdate) -> Reserva:
    """Atualiza a reserva (campos opcionais), revalidando as unicidades CPF+data e mesa+data."""
    reserva = get_reserva(db, reserva_id)

    nome = normalize_nome(payload.nome) if payload.nome is not None else reserva.nome
    cpf = normalize_cpf(payload.cpf) if payload.cpf is not None else reserva.cpf
    telefone = (payload.telefone or "").strip() if payload.telefone is not None else reserva.telefone
    mesa = (payload.mesa or "").strip() if payload.mesa is not None else reserva.mesa
    numero_pessoas = payload.numeroPessoas if payload.numeroPessoas is not None else reserva.numero_pessoas
    data = payload.data if payload.data is not None else reserva.data
    horario = payload.horario if payload.horario is not None else reserva.horario

    if not nome:
        raise ReservaValidationError("Informe seu nome.")
    if len(cpf) != 11:
        raise ReservaValidationError("CPF inválido. Deve conter 11 números.")
    if not telefone:
        raise ReservaValidationError("Informe um telefone de contato.")
    if numero_pessoas < 1:
        raise ReservaValidationError("Informe o número de pessoas.")
    if not mesa:
        raise ReservaValidationError("Selecione uma mesa.")

    if (
        db.scalar(
            select(Reserva).where(Reserva.cpf == cpf, Reserva.data == data, Reserva.id != reserva_id)
        )
        is not None
    ):
        raise ReservaConflictError("Este CPF já possui uma reserva para esta data.")
    if (
        db.scalar(
            select(Reserva).where(Reserva.mesa == mesa, Reserva.data == data, Reserva.id != reserva_id)
        )
        is not None
    ):
        raise ReservaConflictError("Esta mesa já está reservada para este dia.")

    reserva.nome = nome
    reserva.cpf = cpf
    reserva.telefone = telefone
    reserva.numero_pessoas = numero_pessoas
    reserva.data = data
    reserva.horario = horario
    reserva.mesa = mesa
    db.commit()
    db.refresh(reserva)
    return reserva


def list_reservas(db: Session, data: date | None = None) -> list[Reserva]:
    """Lista reservas (filtro opcional por data), ordenadas por horário."""
    stmt = select(Reserva)
    if data is not None:
        stmt = stmt.where(Reserva.data == data)
    stmt = stmt.order_by(Reserva.data.asc(), Reserva.horario.asc(), Reserva.created_at.asc())
    return list(db.scalars(stmt))


def get_reserva(db: Session, reserva_id: UUID) -> Reserva:
    """Busca uma reserva por id (404 quando não existe)."""
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise ReservaNotFoundError()
    return reserva


def delete_reserva(db: Session, reserva_id: UUID) -> None:
    """Exclui a reserva (rota administrativa; exclusão física)."""
    reserva = get_reserva(db, reserva_id)
    db.delete(reserva)
    db.commit()
