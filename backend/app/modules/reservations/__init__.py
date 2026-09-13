"""Módulo `reservations` — reservas, disponibilidade, alocação e status.

Entidades (docs/DOMAIN_SPEC.md §2.6/§2.7/§4.2):
- `Reservation`: núcleo do produto (`date` + `start_time` + `duration_minutes` + `people_count`).
- `ReservationTable`: associação N:N reserva ↔ mesas alocadas (ADR-004).
- `ReservationStatus`: PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW.

Camadas (docs/ARCHITECTURE.md §4):
- `policies`  — funções puras: duração/antecedência/cancelamento/overlap/transições (ADR-010/011).
- `capacity`  — funções puras: `people_count` → mesas necessárias e seleção de mesas (ADR-005).
- `repository`— consultas ORM e bloqueio das mesas (`SELECT ... FOR UPDATE`).
- `service`   — orquestra validação, alocação e transações (criação/edição/cancelamento).
- `router`    — transporte HTTP (contratos em docs/API_SPEC.md §7).

Escopo (Fase 3): **não** implementa horário de funcionamento/grade de slots (D10 aberto),
PreOrder (D1), retenção/cleanup (D11) nem a restrição de reservas simultâneas do mesmo
cliente (R15 — semântica `[TBD]`, não inventada).
"""
