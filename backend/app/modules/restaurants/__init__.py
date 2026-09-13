"""Módulo `restaurants` — restaurante, configuração, mesas e regras de capacidade.

Entidades (docs/DOMAIN_SPEC.md §2.2/§2.3/§2.4/§2.5):
- `Restaurant`: dados do restaurante (o modelo suporta N; a operação é 1 no MVP — D3).
- `RestaurantSettings`: configuração 1:1 com defaults do ADR-010 (cancellation_window_minutes,
  min_booking_lead_minutes, max_booking_lead_days, limites de duração/pessoas).
- `Table`: mesa física (`is_locked` exclui da alocação — R8).
- `CapacityRule`: faixa de pessoas → nº de mesas (ADR-005).

Camadas: router → schema → service → repository (docs/ARCHITECTURE.md §4).

Escopo da Fase 3 (depende de decisões abertas): **não** se implementa `opening_hours` (D10)
nem horário de funcionamento. `Table` reside aqui por ser recurso do restaurante; a
associação com reservas (`ReservationTable`) vive no módulo `reservations`.
"""

