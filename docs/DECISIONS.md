# Blue — Architecture Decision Log (ADR)

> **Propósito:** registrar decisões de produto/arquitetura com justificativa e consequências.
> **Status global:** todas as decisões abaixo estão `Accepted` (vigentes para o MVP). Alterações futuras serão registradas como novo ADR.
> **Estado v1.0 (validação de produto):** D2, D4 e D5 **fechadas** (ADR-010/011/012); D7 e D8 **fechadas** (ADR-013/014) alinhadas ao stack da Fase 2. ADR-015 registra as decisões concretas de implementação da **Fase 2 (Backend Foundation)**. Restam abertas: D1, D3, D6, D9, D10 e D11 (nenhuma bloqueia o início da Fase 2).

## Índice

- [Mapa das decisões](#mapa-das-decisões)
- [ADR-001 — Modular Monolith](#adr-001--modular-monolith)
- [ADR-002 — Python + FastAPI](#adr-002--python--fastapi)
- [ADR-003 — PostgreSQL](#adr-003--postgresql)
- [ADR-004 — Reserva ↔ Mesas via entidade intermediária](#adr-004--reserva--mesas-via-entidade-intermediária)
- [ADR-005 — Alocação por capacidade/regras configuradas](#adr-005--alocação-por-capacidade-regras-configuradas)
- [ADR-006 — Pré-pedido separado de pedido/pagamento](#adr-006--pré-pedido-separado-de-pedidopagamento)
- [ADR-007 — Avaliação ligada a reservas/experiencias elegíveis](#adr-007--avaliacões-ligadas-a-reservas-experiencias-elegíveis)
- [ADR-008 — Notificações in-app](#adr-008--notificações-in-app)
- [ADR-009 — Somente CUSTOMER e ADMIN](#adr-009--somente-customer-e-admin)
- [ADR-010 — Valores padrão de reserva (D2)](#adr-010--valores-padrão-de-reserva-d2)
- [ADR-011 — Overlap de reservas por mesa (D4)](#adr-011--overlap-de-reservas-por-mesa-d4)
- [ADR-012 — Avaliações: uma por reserva concluída (D5)](#adr-012--avaliações-uma-por-reserva-concluída-d5)
- [ADR-013 — Migrações com Alembic (D8)](#adr-013--migrações-com-alembic-d8)
- [ADR-014 — JWT de acesso simples (D7)](#adr-014--jwt-de-acesso-simples-d7)
- [ADR-015 — Fundação do backend: bibliotecas e escopo de models (Fase 2)](#adr-015--fundação-do-backend-bibliotecas-e-escopo-de-models-fase-2)
- [Decisões ainda abertas](#decisões-ainda-abertas)

## Mapa das decisões

| ADR | Título | Status |
| --- | --- | --- |
| ADR-001 | Modular Monolith | ✅ Accepted |
| ADR-002 | Python + FastAPI | ✅ Accepted |
| ADR-003 | PostgreSQL | ✅ Accepted |
| ADR-004 | Reserva ↔ mesas via entidade intermediária | ✅ Accepted |
| ADR-005 | Alocação por capacidade/regras configuradas | ✅ Accepted |
| ADR-006 | Pré-pedido separado de pedido/pagamento | ✅ Accepted |
| ADR-007 | Avaliação ligada a reservas/experiencias | ✅ Accepted |
| ADR-008 | Notificações in-app | ✅ Accepted |
| ADR-009 | Somente CUSTOMER e ADMIN | ✅ Accepted |
| ADR-010 | Valores padrão de reserva (D2) | ✅ Accepted |
| ADR-011 | Overlap de reservas por mesa (D4) | ✅ Accepted |
| ADR-012 | Avaliações: uma por reserva concluída (D5) | ✅ Accepted |
| ADR-013 | Migrações com Alembic (D8) | ✅ Accepted |
| ADR-014 | JWT de acesso simples (D7) | ✅ Accepted |
| ADR-015 | Fundação do backend (libs e escopo de models) | ✅ Accepted |

---

## ADR-001 — Modular Monolith

**Status:** Accepted

**Decision:**

Utilizar um **monólito modular** como arquitetura do backend do Blue, em lugar de microsserviços, para todo o alcance do MVP.

**Reasoning:**

- O domínio é pequeno (reservas, cardápio, pré-pedidos, avaliações, eventos) e a equipe pequena; microsserviços adicionam complexidade distribuída sem benefício claro no MVP.
- Módulos bem delimitados preservam a possibilidade de extrair serviços no futuro sem custo desmedido.
- Menor custo operativo (deploy, observabilidade, testes).

**Consequences:**

- O código organiza-se por módulos (auth, users, restaurants, reservations, menu, preorders, reviews, events, notifications).
- As dependências entre módulos devem ser mínimas e explícitas (via services/interfaces).
- Um único deployable de aplicação; não se criam barreras físicas de deploy no MVP.
- Revisar a decisão se o domínio crescer para áreas independientes.

---

## ADR-002 — Python + FastAPI

**Status:** Accepted

**Decision:** Adotar **Python + FastAPI** como framework HTTP do backend.

**Reasoning:** Framework moderno, tipado (Pydantic), documentação OpenAPI automática, alta velocidade de desenvolvimento e maturidade da comunidade — adequado para uma equipe pequena.

**Consequences:**

- Schemas com Pydantic; validação na borda da API.
- Autenticação/autorização seguindo o padrão de dependências de FastAPI.
- `pyproject.toml` como fonte de projeto/dependências.
- Regras de negócio nos services/domain, nunca nos routers.

---

## ADR-003 — PostgreSQL

**Status:** Accepted

**Decision:** **PostgreSQL** como base de dados relacional principal.

**Reasoning:** O domínio exige integridade forte (reservas, unicidade de slots, regras de capacidade), transações, constraints e consistência em concorrencia.

**Consequences:**

- Migrações versionadas de schema (ferramenta `[TBD]` — ver D8).
- A alocação de mesas sem solapamento exige transações + constraints (ver ADR-005 e `DOMAIN_SPEC.md` §5).
- Backup e resiliencia de dados operativos (reservas, pré-pedidos, avaliações).

---

## ADR-004 — Reserva ↔ Mesas via entidade intermediária

**Status:** Accepted

**Decision:** Modelar a relação `Reservation N:N Table` através da entidade associativa **`ReservationTable`**.

**Reasoning:** Uma reserva pode alocar várias mesas e uma mesa pode participar em várias reservas em horários distintos. A entidade intermediária documenta a alocação por reserva.

**Consequences:**

- `ReservationTable` leva `reservation_id` e `table_id`, com unicidade por par.
- A alocação é **resultado** da reserva, não uma escolha manual de mesas (a diferença do frontend atual).
- Cardinalidade e unicidade documentadas em `DOMAIN_SPEC.md` §3.

---

## ADR-005 — Alocação por capacidade/regras configuradas

**Status:** Accepted

**Decision:** A **quantidade de pessoas** determina as mesas necessárias via **`CapacityRule`** configurada pelo restaurante; o sistema aloca dinámicamente mesas disponíveis. Não se modelam combinações físicas fixas de mesas no MVP.

**Reasoning:** Eliminar a escolha manual de mesas (frágil e ineficiente) e permitir que o restaurante expresse "pessoas → nº de mesas" mediante regras, sem modelar geometria do salão.

**Consequences:**

- `CapacityRule` (faixa de pessoas → nº de mesas) é fonte de verdade para a alocação.
- A validação anti-solapamento deve ser atómica na base (transação + constraint).
- Mesas bloqueadas pelo admin ficam excluidas da alocação.
- O frontend atual (escolha manual de mesas) será substituído por alocação automática.

---

## ADR-006 — Pré-pedido separado de pedido/pagamento

**Status:** Accepted

**Decision:** O **pré-pedido** é um conceito separado do pedido/checkout e do pagamento. **Pagamento não faz parte do MVP.**

**Reasoning:** O MVP não contempla pagamento nem delivery; separar os domínios evita contaminar o modelo de reservas com regras de facturação não definidas.

**Consequences:**

- `PreOrder`/`PreOrderItem` referenciam a reserva e items do cardápio (snapshot de preço — ver `DOMAIN_SPEC.md`).
- Não construir checkout/payment no MVP (`[FUTURE]`; requer novo ADR quando definido).
- `PreOrderStatus`: `DRAFT`, `SUBMITTED`, `CONFIRMED`, `CANCELLED`.

---

## ADR-007 — Avaliação ligada a reservas/experiencias elegíveis

**Status:** Accepted

**Decision:** As avaliações só podem ser criadas **após a experiência** (reserva concluída); a avaliação de um prato só é possível se o prato esteja associado àquela experiência (pré-pedido elegível).

**Reasoning:** Dar relevância às avaliações (evita avaliações inventadas) e restringir a avaliação de pratos a quem realmente os consumiu.

**Consequences:**

- `Review.reservation_id` é um campo requerido.
- `ReviewItem` referencia `Review` e `MenuItem` e está condicionada ao pré-pedido da reserva.
- Moderação (publicar/ocultar) e resposta do admin fazem parte do MVP.
- Status `PUBLISHED` / `HIDDEN` (ver `DOMAIN_SPEC.md` §4).

---

## ADR-008 — Notificações in-app

**Status:** Accepted

**Decision:** O MVP inicia as notificações **in-app** (dentro da aplicação). E-mail fica como possibilidade futura.

**Reasoning:** Menor complexidade; um centro de notificações já existe como conceito no frontend; o e-mail agrega dependências (provedor, templates, consentimento) sem necessidade no MVP.

**Consequences:**

- Modelo `Notification` e endpoints in-app (ver `API_SPEC.md` §13).
- E-mail/push permanecem como `[FUTURE]`.
- Fontes de emissão: reserva, pré-pedido, avaliação, evento, admin.

---

## ADR-009 — Somente CUSTOMER e ADMIN no MVP

**Status:** Accepted

**Decision:** No MVP existem **somente** os roles `CUSTOMER` e `ADMIN`.

**Reasoning:** Simplicidade; evita regras de autorização de níveis intermedios que o alcance não exige.

**Consequences:**

- Enum `UserRole` limitado a dois valores.
- Não criar níveis intermedios (hostess, garçom, gerente de salão) sem novo ADR.
- Autorização por role em todos os endpoints (ver `API_SPEC.md` §3).

---

## ADR-010 — Valores padrão de reserva (D2)

**Status:** Accepted

**Decision:**

Adotar os seguintes valores padrão de reserva (defaults do restaurante, configurables pelo ADMIN via `RestaurantSettings`):

| Parâmetro | Valor padrão |
| --- | --- |
| Duração mínima | 30 minutos |
| Duração máxima | 3 horas (180 minutos) |
| Incremento de duração | 30 minutos |
| Antecedência mínima para reservar | 1 hora (60 minutos) |
| Antecedência máxima | 90 dias |
| Cancelamento permitido até | 1 hora (60 minutos) antes do início |

Estes valores **não são constantes do domínio**: residem em `RestaurantSettings` e o service lê a configuração do restaurante, nunca valores fixos do código.

**Reasoning:** dar um ponto de partida operacional consistente sem engessar o domínio; o ADMIN pode alterar os valores posteriormente sem mudança de código.

**Consequences:**

- `RestaurantSettings` ganha dois campos: `min_booking_lead_minutes` (default 60) e `max_booking_lead_days` (default 90).
- Defaults dos campos existentes de settings: `cancellation_window_minutes = 60`, `reservation_min_duration_minutes = 30`, `reservation_max_duration_minutes = 180`, `reservation_duration_step_minutes = 30`.
- Atualizar `DOMAIN_SPEC.md` §2.3 e `API_SPEC.md` §6/§7 (availability, POST/PATCH `/reservations`).

---

## ADR-011 — Overlap de reservas por mesa (D4)

**Status:** Accepted

**Decision:**

Uma mesma **mesa física** não pode estar associada a duas reservas cujos intervalos de tempo se sobreponham. Intervalo = `[start_time, start_time + duration_minutes)`; duas reservas se sobrepõem se `start_A < end_B` e `start_B < end_A`.

```text
19:00 → 21:00   [ocupa a mesa]
21:00 → 23:00   [adjacente → PERMITIDO na mesma mesa]
```
```text
19:00 → 21:00   [ocupa a mesa]
20:00 → 22:00   [sobrepõe → INVÁLIDO na mesma mesa]
```

- Intervalos adjacentes são permitidos; **sem buffer inter-slot** no MVP.
- A validação ocorre no **backend**.
- A operação de criação/alocação de reserva (e edição/re-alocação) é **transacional**, evitando race conditions em reservas simultâneas.

**Reasoning:** a unidade de conflito é a mesa; margem de limpeza entre slots pode ser adicionada futuramente como configuração sem alterar o modelo.

**Consequences:**

- Overlap → `409 Conflict` em criação/edição.
- Criação/alocação em uma única transação com bloqueio das mesas candidatas (`SELECT ... FOR UPDATE`) e/ou constraint de exclusão no PostgreSQL.
- Atualizar `DOMAIN_SPEC.md` §5.1, `API_SPEC.md` §7 e regra R9 em `PRODUCT_SPEC.md`.

---

## ADR-012 — Avaliações: uma por reserva concluída (D5)

**Status:** Accepted

**Decision:**

- Uma **avaliação de restaurante por reserva concluída**: cada reserva gera no máximo uma avaliação de restaurante.
- O cliente pode avaliar **pratos elegíveis** associados à experiência (pré-pedido da reserva).
- Cada prato pode ser avaliado **uma única vez** dentro daquela avaliação.
- Avaliações só podem ser criadas após a reserva estar `COMPLETED`.
- O cliente **não pode** avaliar arbitrariamente um prato que não esteja associado à experiência elegível.
- `ADMIN` pode moderar (`PUBLISHED`/`HIDDEN`) e responder.
- **Não** é permitida edição da avaliação no MVP.

**Reasoning:** garantir relevância e integridade das avaliações e restringir avaliação de pratos a quem efetivamente os consumiu.

**Consequences:**

- Constraints na DB: `Review.reservation_id` único (uma avaliação de restaurante por reserva); `UNIQUE(review_id, menu_item_id)` em `ReviewItem`.
- Sem endpoint de edição de conteúdo da avaliação (sem `PATCH/DELETE /reviews/{id}` de conteúdo no MVP).
- `Review.responded_at` definido: preenchido junto com `admin_response`.
- Atualizar `DOMAIN_SPEC.md` §2.12/§2.13 e §3; `API_SPEC.md` §11; `PRODUCT_SPEC.md` §3.6 e R18.

---

## ADR-013 — Migrações com Alembic (D8)

**Status:** Accepted

**Decision:** Usar **Alembic** (integrado ao SQLAlchemy) para migrações versionadas do schema.

**Reasoning:** o stack da Fase 2 já define SQLAlchemy; Alembic é a ferramenta padrão do ecossistema e o controle de versão do schema é necessário já na Fase 2.

**Consequences:**

- Estrutura `backend/migrations/` com Alembic (ver `ARCHITECTURE.md` §3).
- Política de retenção/cleanup de dados passa a ser decisão separada — D11 (aberta).

---

## ADR-014 — JWT de acesso simples (D7)

**Status:** Accepted

**Decision:** **JWT access token** de curta duração, **sem refresh token** no MVP.

**Reasoning:** simplicidade e escopo do MVP; refresh token adiciona estado/rotação sem necessidade imediata (reavaliar pós-MVP).

**Consequences:**

- `POST /auth/login` devolve `access_token`; expiração configurável.
- Sem endpoint `/auth/refresh` no MVP.
- Atualizar `API_SPEC.md` §2/§3 e `ARCHITECTURE.md` §6.

---

## ADR-015 — Fundação do backend: bibliotecas e escopo de models (Fase 2)

**Status:** Accepted

**Decision:**

Na **Fase 2 (Backend Foundation)** adotam-se as seguintes decisões concretas de implementação:

- **JWT:** biblioteca **PyJWT** (HS256) — reforça ADR-014 (access token sem refresh).
- **Password hashing:** **Argon2** via `pwdlib` (`PasswordHash.recommended()`); a senha é
  armazenada somente como hash (docs/DOMAIN_SPEC.md §2.1).
- **Driver PostgreSQL:** **psycopg v3** (`postgresql+psycopg://`) com SQLAlchemy 2 (síncrono).
- **Enum de role:** `UserRole` persistido como `VARCHAR` (`native_enum=False`), sem tipo enum
  nativo PostgreSQL, para manter o schema portável no MVP.
- **Escopo inicial de models:** somente **`User`** (necessário à fundação de autenticação).
  `Restaurant`, `RestaurantSettings`, `CapacityRule` e demais entidades **não** são criados na
  Fase 2 — entram junto com os módulos de negócio que os consomem (Fases 3+), evitando models
  especulativos.
- **Endpoints da fundação:** `GET /health`, `GET /health/db` e `/auth/register|login|me`
  (contracts de docs/API_SPEC.md §4). Módulo `restaurants/` permanece como scaffold.
- **Estratégia de testes:** testes unitários não exigem banco; testes de integração
  (ORM/migrations/auth end-to-end) exigem um PostgreSQL real via `DATABASE_URL` e são **pulados**
  quando indisponível — **sem SQLite como substituto** do PostgreSQL em testes.

**Reasoning:** manter a fundação executável e verificável com o mínimo de dependências;
não modelar domínio antes das fases que o consomem; não simular sucesso de PostgreSQL
onde ele não existe.

**Consequences:**

- Primeira migration Alembic contém apenas a tabela `users` (ver `backend/migrations/versions/`).
- Camadas router → schema → service → repository demonstradas em `auth`/`users`
  (docs/ARCHITECTURE.md §4).
- Estrutura de testes em `backend/tests/` com marker `integration`.
- Decisões abertas D6 (seed do primeiro `ADMIN`) e D9 (CI mínimo) permanecem e não bloqueiam
  a fundação (ver docs/ROADMAP.md — Fase 2).

---

## Ajustes de consistência do domínio (v1.0)

Ajustes menores da revisão de coerência entre `DOMAIN_SPEC.md`, `PRODUCT_SPEC.md`, `API_SPEC.md` e `ARCHITECTURE.md` — não alteram arquitetura, apenas fecham campos `[TBD]`/`[PROPOSTA]`:

- `RestaurantSettings`: novos campos `min_booking_lead_minutes` (default 60) e `max_booking_lead_days` (default 90) — ver ADR-010.
- `Notification`: campo `updated_at` adicionado (`is_read` é mutável) — padrão de auditoria uniforme.
- `PreOrderItem` e `ReviewItem`: linhas **append-only** — recebem `created_at` e **não** recebem `updated_at`.
- `Reservation`: `cancelled_by` (enum `UserRole`) e `cancelled_at` confirmados — preenchidos no cancelamento (R12/R13).
- `Review`: `responded_at` confirmado — preenchido junto com `admin_response` (ADR-012).

---

## Decisões ainda abertas

| # | Tema | Estado |
| --- | --- | --- |
| D1 | `Reservation ↔ PreOrder` (1:1 vs 1:N) | `[TBD]` |
| D2 | Valores padrão de reserva | ✅ **CLOSED** → ADR-010 |
| D3 | Múltiplos restaurantes por instância (operação multi-restaurante do admin) | `[TBD]` |
| D4 | Overlap de reservas / buffer inter-slot | ✅ **CLOSED** → ADR-011 (sem buffer no MVP) |
| D5 | Quantas avaliações por reserva e regras de `ReviewItem` | ✅ **CLOSED** → ADR-012 |
| D6 | Bootstrap do primeiro `ADMIN` (seed) | `[TBD]` |
| D7 | Token JWT simple vs JWT + refresh | ✅ **CLOSED** → ADR-014 (access token sem refresh no MVP) |
| D8 | Ferramenta de migrações e política de dados | ✅ **CLOSED** (ferramenta) → ADR-013 (Alembic); política de dados → D11 |
| D9 | Testes/CI, deploy e observabilidade | `[TBD]` |
| D10 | Horários de funcionamento do restaurante (janelas de reserva) | `[TBD]` |
| D11 | Política de retenção/cleanup de dados (borrado lógico vs físico, retenção de notificações) | `[TBD]` (desmembrada de D8) |

> **Observações:** nenhuma das decisões abertas (D1, D3, D6, D9, D10, D11) bloqueia o início da Fase 2 — ver `ROADMAP.md`. R15 (`PRODUCT_SPEC.md` §5.1) também permanece com semântica exata `[TBD]` (reservas simultâneas do mesmo cliente), sem bloquear o modelo de dados nem a Fase 2.

> **Regra:** quando se decida um `[TBD]`, registra-se como novo ADR neste arquivo e atualiza-se `DOMAIN_SPEC.md`/`API_SPEC.md`.