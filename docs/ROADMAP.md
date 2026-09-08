# Blue — Roadmap v1.0

> **Status geral:** Fase 0 `DONE` (produto e domínio validados); Fase 2 `IN PROGRESS`
> (foundation implementada — ver seção; encerramento depende de PostgreSQL real e de D6/D9);
> Fases 1 e 3–8 ainda `TODO`.
> Este é um **plano técnico**. Ver `PRODUCT_SPEC.md` para *o quê* e `DECISIONS.md` para o *porquê*. Fases dependem dos `[TBD]` fechados (ver fim de `DECISIONS.md`).

## Legenda

| Símbolo | Significado |
| --- | --- |
| `TODO` | Ainda não iniciado. |
| `IN PROGRESS` | Em andamento. |
| `DONE` | Concluído. |
| `[TBD]` | Decisão necessária antes de prosseguir. |

## Visão geral

| Fase | Nome | Status |
| --- | --- | --- |
| 0 | Product & Domain | `DONE` |
| 1 | Frontend Architecture | `TODO` |
| 2 | Backend Foundation | `IN PROGRESS` |
| 3 | Reservations | `TODO` |
| 4 | Menu | `TODO` |
| 5 | Pre-orders | `TODO` |
| 6 | Reviews | `TODO` |
| 7 | Events | `TODO` |
| 8 | Notifications | `TODO` |

---

## Fase 0 — Product & Domain

**Status:** `DONE`

- [x] Produto: visão, usuários, funcionalidades, fluxos e regras (`PRODUCT_SPEC.md`).
- [x] Regras de negócio de reserva (capacidade, overlap, cancelamento) — §5 do `PRODUCT_SPEC.md` e §5 do `DOMAIN_SPEC.md`.
- [x] Domínio: entidades, enums e relacionamentos (`DOMAIN_SPEC.md`).
- [x] Decisões de arquitetura (`DECISIONS.md` — ADR-001 a ADR-014).
- [x] Fechamento das decisões bloqueantes: D2 (defaults), D4 (overlap) e D5 (avaliações) → ADR-010/011/012; D7 (JWT) e D8 (Alembic) → ADR-013/014 (ver `DECISIONS.md`).
- **Decisões abertas (não bloqueiam a Fase 2):** D1 (pré-pedido), D3 (multi-restaurante), D6 (seed admin), D9 (CI/deploy/observabilidade), D10 (horários), D11 (retenção de dados) — ver `DECISIONS.md`.

**Critério de saída (cumprido):** nenhum `[TBD]` crítico bloqueando modelo de dados e contrato de API.

---

## Fase 1 — Frontend Architecture

**Status:** `TODO`

Objetivos (não altera regras de negócio; prepara o terreno para consumir o backend):

- [ ] Modularizar o fluxo de reservas em `src/features/reservations/` (deixar de depender de modais/state espalhados em `App.tsx`/`Pages`).
- [ ] Remover dependência direta de `localStorage` das regras (extrair acesso a dados para abstrações).
- [ ] Criar abstração de storage (interface com implementações: `localStorage` hoje; servidor depois).
- [ ] Preparar API client tipado (base URL, interceptors, tratamento de erro) (sem endpoints ainda — `[PLANNED]`).
- [ ] Testes de regras (lógica de capacidade, disponibilidade, overlap) em módulo isolado.

**Critério de saída:** regras de reserva testáveis e independentes de UI/storage; build/lint verdes.

---

## Fase 2 — Backend Foundation

**Status:** `IN PROGRESS`

> A **fundação** está implementada e executável (código em `backend/`). O encerramento
> da fase depende de (a) verificação contra um **PostgreSQL real** — o ambiente de dev
> atual não possui PostgreSQL/Docker, então migrations e login end-to-end ficam
> pendentes (sem simulação) — e (b) das decisões abertas D6 (seed do primeiro `ADMIN`)
> e D9 (CI mínimo).

- [x] Estrutura `backend/` (modular monolith — `ARCHITECTURE.md` §3), com `app/core`,
      `app/modules/{auth,users,restaurants}`, `app/shared`, `migrations/`, `tests/`.
- [x] **Python** + **FastAPI** + **PostgreSQL** + **SQLAlchemy 2** configurados
      (engine, session factory, `Base` e dependency `get_db` via `DATABASE_URL`).
- [x] Configuração por ambiente (pydantic-settings; `.env.example`; sem credenciais no Git).
- [x] Logging básico configurado por `LOG_LEVEL`.
- [x] Migrations com **Alembic** (D8 — ADR-013): `env.py` importa o metadata real dos models;
      primeira migration criada: tabela `users`.
- [ ] `alembic current` / `alembic upgrade head` executados contra PostgreSQL real —
      **bloqueado por ambiente** (sem PostgreSQL/Docker disponível; renderização offline
      validada no dialeto PostgreSQL).
- [x] JWT access token **sem refresh** (D7 — ADR-014); password hashing (Argon2 via
      `pwdlib`); senha armazenada somente como hash.
- [x] Roles `CUSTOMER`/`ADMIN` (ADR-009) e dependency de autorização por role.
- [x] Camadas router → schema → service → repository (foundation demonstrada em
      `auth`/`users` — ver `ARCHITECTURE.md` §4).
- [x] `/auth`: registro de cliente, login e `/auth/me` (foundation; contratos de
      `API_SPEC.md` §4). **Criação/seed do primeiro `ADMIN`**: pendente (D6 `[TBD]`).
- [x] Modelo `User` (foundation de autenticação) — demais models entram com os módulos de
      negócio (Fases 3+; ver ADR-015). Módulo `restaurants/` criado como scaffold.
- [x] Health checks: `GET /health` (API) e `GET /health/db` (PostgreSQL).
- [x] Testes base (**pytest**): unitários sem banco (config, JWT, hashing, roles, health,
      app) e testes de integração marcados que são pulados quando o PostgreSQL está
      indisponível (`pytest`: 19 passed, 6 skipped no ambiente atual).
- [ ] CI mínimo — pendente (D9 `[TBD]`).

**Critério de saída:** servidor sobe ✅ · health-check ✅ · banco com migrations ⏳
(bloqueado por ambiente) · login funcional ⏳ (bloqueado por ambiente).

---

## Fase 3 — Reservations

- [ ] `Table` (CRUD admin) e `CapacityRule`.
- [ ] Disponibilidade (slots por data/horário; regras de overlap por mesa — `DOMAIN_SPEC` §5.1, ADR-011).
- [ ] Validações de duração/antecedência lidas de `RestaurantSettings` (ADR-010: defaults 30–180 min, passo 30 min; antecedência 1 h a 90 dias).
- [ ] Criação de reserva com alocação dinâmica via `ReservationTable` — **transacional** (ADR-011).
- [ ] Edição de reserva (data/horário/duração/pessoas com revalidação).
- [ ] Cancelamento (cliente/admin) dentro da janela configurada (default 1 h antes do início — ADR-010).
- [ ] Status: `PENDING` → `CONFIRMED` → `COMPLETED` / `NO_SHOW`; `CANCELLED`.
- [ ] Endpoints `[PLANNED]` — ver `API_SPEC.md` §7.

**Critério de saída:** fluxo completo de reserva funcional contra o banco.

---

## Fase 4 — Menu

- [ ] `MenuCategory` e `MenuItem` (preço, descrição, imagem, disponibilidade).
- [ ] Disponibilidade/ativação de itens.
- [ ] Endpoints públicos de consulta e admin de gestão (`API_SPEC.md` §9).
- [ ] Compatibilidade com o widget de cardápio do frontend (substituir cardápio estático).

**Critério de saída:** cardápio vem do backend; itens inativos não aparecem.

---

## Fase 5 — Pre-orders

- [ ] `PreOrder` + `PreOrderItem` vinculados à reserva.
- [ ] Criação, edição de itens, envio (`SUBMITTED`), confirmação e cancelamento.
- [ ] Regras `[TBD]` (D1, quota/itens; limitação por reserva).
- [ ] Endpoints `API_SPEC.md` §10.

---

## Fase 6 — Reviews

- [ ] Avaliação de restaurante vinculada a reserva concluída (ADR-007); **uma** avaliação por reserva (`UNIQUE reservation_id` — ADR-012).
- [ ] Avaliação de pratos elegíveis (`ReviewItem`) a partir do pré-pedido; cada prato uma única vez por avaliação (`UNIQUE review_id, menu_item_id` — ADR-012).
- [ ] Moderação (publicar/ocultar) e resposta pelo admin.
- [ ] **Sem edição** de avaliação no MVP (ADR-012).
- [ ] Endpoints `API_SPEC.md` §11.

---

## Fase 7 — Events

- [ ] `EventRequest` com fluxo `PENDING` → `APPROVED`/`REJECTED`/`CANCELLED`.
- [ ] Painel admin de eventos.
- [ ] Endpoints `API_SPEC.md` §12.

---

## Fase 8 — Notifications

- [ ] Emissão in-app (`IN_APP`) a partir de eventos de domínio (reserva, pré-pedido, avaliação, evento, admin).
- [ ] Centro de notificações (listar, marcar como lida, limpar).
- [ ] Endpoints `API_SPEC.md` §13.
- [ ] E-mail fica como possibilidade **futura** (`[FUTURE]`) — não implementar no MVP (ADR-008).

---

> Fim de `ROADMAP.md`.