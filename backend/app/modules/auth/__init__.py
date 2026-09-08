"""Módulo `auth` — autenticação (foundation da Fase 2).

Escopo desta fase (docs/ROADMAP.md — Fase 2):
- Registro de cliente (CUSTOMER), login e perfil da sessão, conforme
  docs/API_SPEC.md §4.
- JWT access token sem refresh (ADR-014).
- Criação de ADMIN fica pendente de decisão de seed (D6 [TBD]) — sem endpoint aqui.

Fluxos completos de negócio (recuperação de senha, refresh etc.) não fazem
parte desta fase nem do MVP (docs/DECISIONS.md — ADR-014).
"""
