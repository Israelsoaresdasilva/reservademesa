"""Exceções de aplicação mapeadas para HTTP pela camada API.

Fonte: docs/API_SPEC.md §2 (erros padrão: 400, 401, 403, 404, 409, 422).
Os handlers globais ficam registrados em app/main.py.
"""


class AppError(Exception):
    """Erro de domínio/aplicação com status HTTP correspondente."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class UnauthorizedError(AppError):
    """401 — não autenticado / credenciais inválidas."""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(401, detail)


class ForbiddenError(AppError):
    """403 — autenticado mas sem permissão (role inadequada)."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(403, detail)


class NotFoundError(AppError):
    """404 — recurso não encontrado."""

    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(404, detail)


class ConflictError(AppError):
    """409 — conflito de disponibilidade/duplicidade/estado."""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(409, detail)
