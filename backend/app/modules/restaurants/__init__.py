"""Módulo `restaurants` — scaffold da fundação (sem models nesta fase).

Responsabilidade futura (docs/ARCHITECTURE.md §3): `Restaurant`,
`RestaurantSettings` e `CapacityRule` (docs/DOMAIN_SPEC.md §2.2/§2.3/§2.5).

Decisão de Fase 2 (ver ADR-015): o model `Restaurant` **não** foi criado nesta
fase porque a fundação de autenticação não depende dele — os models de restaurante
entram junto com os módulos de negócio (Fase 3+) para evitar modelos especulativos.
"""
