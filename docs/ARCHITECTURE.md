# Blue — Architecture v1.0

> **Status:** este documento descreve (a) o **estado atual** — frontend React com dados simulados — e (b) a **arquitetura alvo** — modular monolith com backend Python/FastAPI/PostgreSQL.

## Convenções de estado

| Tag | Significado |
| --- | --- |
| `[CURRENT]` | Existe hoje no repositório. |
| `[PLANNED]` | Direção alvo, planejada, não existe hoje. |
| `[DECISION]` | Decisão de arquitetura já tomada (ver `DECISIONS.md`). |
| `[TBD]` | Decisão aberta. |

## Índice

1. [Estado atual](#1-estado-atual)
2. [Princípios e arquitetura alvo](#2-princípios-e-arquitetura-alvo)
3. [Backend — estrutura inicial](#3-backend--estrutura-inicial)
4. [Camadas backend](#4-camadas-backend)
5. [Frontend — direção](#5-frontend--direção)
6. [Comunicação Frontend → Backend](#6-comunicação-frontend--backend)
7. [Dados e persistência](#7-dados-e-persistência)
8. [Documentação relacionada](#8-documentação-relacionada)

---

## 1. Estado atual

### Stack atual

```
Frontend
React 19
TypeScript
Vite
Three.js / React Three Fiber (mapa do salão em 3D)
```

### O que existe hoje (`[CURRENT]`)

- Landing page de "Ocean Blue" com widget de cardápio flotante e modais de reservas/avaliações. Todo é SPA com estado cliente-side.
- **Reservas simuladas:** seleção manual de mesas sobre o mapa 3D, com dados em `localStorage`. Não há conta, horário, duração nem quantidade de pessoas.
- **Mesas:** `DEFAULT_MESAS` (23 mesas) + calibração via mapa 3D (`CalibrateMode`, `MapFloor`) com export JSON (`table-map.json`).
- **Cardápio:** array estático em `homepage.tsx` (widget estilo chat); existe também `public/Cardápio.html` legado.
- **Avaliações:** lista mockada + formulário que adiciona avaliação em memória (sem persistência).
- **Eventos:** formulário simples que apenas mostra um pop-up de confirmação.
- **Notificações:** provider via React Context em memória, limite de 20 itens, sem persistência.

### LocalStorage atualmente usado

| Chave | Conteúdo |
| --- | --- |
| `mesas_calibradas` | Mesas calibradas pelo mapa 3D. |
| `mesas_reservadas_v2` | Reservas simuladas. |
| `dataReserva` | Data escolhida no fluxo de reserva. |
| `ultima_reserva_confirmada_v2` | Última reserva confirmada. |

### Limitações do estado atual

1. Não há backend, banco de dados, autenticação nem API.
2. Todo o modelo de regra de negócio de reserva é client-side e manipulável (qualquer usuário pode alterar `localStorage`).
3. Mesas "bloqueadas" por dia são geradas por heurística a partir da data, não por regras reais do restaurante.
4. Não existe pré-pedido, avaliação de pratos, moderação, status de eventos nem status de reservas.
5. Não existe conceito de usuário, role ou autenticação.

**Implicação:** nada descrito como `[PLANNED]` existe ainda.

---

## 2. Princípios e arquitetura alvo

### Princípios

1. **Backend real com dados persistentes** — substituir a simulação client-side por API + PostgreSQL.
2. **Modular monolith** (ADR-001) — um único deploy com módulos bem delimitados; **não** se usam microsserviços no MVP.
3. **Regras de negócio no backend** (services/domain) — o frontend não decide disponibilidade, capacidade, overlap nem cancelamento.
4. **API-first** — o frontend consume os contratos definidos em `API_SPEC.md`; OpenAPI gerada pelo FastAPI.
5. **Evolução incremental** — as fases do `ROADMAP.md` substituem funcionalidades simuladas sem quebrar a experiência atual.

### Arquitetura alvo (visão)

```
Frontend (React + TypeScript + Vite)
        |  HTTP/JSON (+ auth bearer)
        v
FastAPI   (modular monolith)
        |
        v
PostgreSQL
```

- Comunicação síncrona REST no MVP. Realtime/websocket para notificações: `[TBD]` (inicialmente polling in-app — ver `API_SPEC.md` §13).
- Migrations versionadas com **Alembic** (D8 — ADR-013).
- Um único container de aplicação; banco de dados separado.

---

## 3. Backend — estrutura inicial

```
backend/
├── app/
│   ├── main.py                  # app FastAPI, roteadores, lifespan
│   ├── core/                    # config (settings), db (engine/session), security (jwt, hash), exceptions
│   ├── modules/
│   │   ├── auth/                # registro, login, tokens, dependência current_user
│   │   ├── users/               # User, UserRole, perfil
│   │   ├── restaurants/         # Restaurant, RestaurantSettings, CapacityRule
│   │   ├── reservations/        # Reservation, ReservationTable, availability, alocação
│   │   ├── menu/                # MenuCategory, MenuItem
│   │   ├── preorders/           # PreOrder, PreOrderItem
│   │   ├── reviews/             # Review, ReviewItem, moderação, resposta
│   │   ├── events/              # EventRequest, workflow admin
│   │   └── notifications/       # Notification, emissor in-app
│   └── shared/                  # utilidades comuns (datas, enums, query helpers, dto base)
├── migrations/                  # schema versionado (Alembic — ADR-013)
├── tests/                       # testes por módulo
└── pyproject.toml               # projeto/ferramentas (uv/poetry/hatch — escolha PROPOSTA)
```

### Responsabilidade de cada módulo

| Módulo | Responsabilidade | Entidades principais |
| --- | --- | --- |
| `auth` | Registro, login, emissão/validação de token, dependência de autenticação. | — (usa `users`) |
| `users` | `User`, `UserRole`, perfil e CRUD próprio. | `User` |
| `restaurants` | Dados do restaurante, settings e `CapacityRule`. | `Restaurant`, `RestaurantSettings`, `CapacityRule` |
| `reservations` | Disponibilidade, overlap, alocação via `ReservationTable`, edit/cancel, status. | `Reservation`, `ReservationTable` |
| `menu` | Categorias e itens do cardápio, disponibilidade. | `MenuCategory`, `MenuItem` |
| `preorders` | Pré-pedido, itens, transições de estado. | `PreOrder`, `PreOrderItem` |
| `reviews` | Avaliação do restaurante e de pratos, moderação, resposta. | `Review`, `ReviewItem` |
| `events` | Solicitação de evento e workflow de aprovação. | `EventRequest` |
| `notifications` | Emissão/consulta de notificações in-app. | `Notification` |

---

## 4. Camadas backend

Dentro de cada módulo, separar responsabilidades com este fluxo:

```
API / Router
      |
      v
Schema        (Pydantic: request/response DTOs)
      |
      v
Service       (casos de uso + regras de negócio)
      |
      v
Repository    (consulta a dados/ORM)
      |
      v
Database      (PostgreSQL)
```

Regras:

- **Routers**: recepção do request, validação via schema, chamada ao service e serialização da resposta. Nunca contêm regras de negócio.
- **Services**: contêm as regras de negócio (overlap por mesa, capacidade, janela de cancelamento/antecedência, elegibilidade de avaliações, transições de estado) e coordenam operações **transacionais** (criação/re-alocação de reserva — ADR-011).
- **Repositories**: encapsulam as querys; caso se use ORM, o repository é a fronteira.
- Exceções de domínio mapeadas a códigos HTTP segundo `API_SPEC.md` §2 (409 para conflitos de disponibilidade/duplicidade).

---

## 5. Frontend — direção

O frontend atual (React 19 + TypeScript + Vite) evoluciona para uma estrutura por **features**:

```
src/
├── features/
│   ├── reservations/
│   ├── menu/
│   ├── reviews/
│   ├── events/
│   ├── notifications/      # já existe (provider + centro)
│   └── auth/               # nova
├── api-client/             # cliente HTTP tipado (PLANNED)
├── pages/                  # composição da UI atual
└── App.tsx
```

Regras de evolução (Fase 1 do `ROADMAP.md`):

1. Regras de negócio que hoje estão no frontend **não** se reimplementam para o MVP; passam ao backend.
2. `localStorage` é considerado **storage temporário/abstração**, não fonte de verdade.
3. O `api-client` deve permitir trocar o storage atual por chamadas à API sem mudanças na UI.

---

## 6. Comunicação Frontend → Backend

```
Frontend
   |
   v
API Client   (fetch/axios — escolha PROPOSTA; interceptores de auth/erros)
   |
   v
FastAPI      (modular monolith)
   |
   v
Database     (PostgreSQL)
```

- Formato JSON; auth com `Authorization: Bearer <token>` (JWT access token sem refresh no MVP — ADR-014).
- Erros normalizados (ver `API_SPEC.md` §2).
- Notificações: inicialmente via **polling** de `GET /notifications` (in-app; ADR-008); websocket `[TBD]`.

---

## 7. Dados e persistência

- **PostgreSQL** (ADR-003) — única fonte de verdade.
- Migrations versionadas com **Alembic** (D8 — ADR-013).
- Constraints críticos: unicidade de e-mail (`User`); unicidade `(reservation_id, table_id)` em `ReservationTable`; `Review.reservation_id` único (uma avaliação de restaurante por reserva — ADR-012); `UNIQUE(review_id, menu_item_id)` em `ReviewItem` (ADR-012); anti-overlap por mesa validado de forma **transacional** na alocação (ADR-011 — ver `DOMAIN_SPEC.md` §5.1).
- Cleanup/retention de dados (notificações, eliminados) — `[TBD]` (D11).

---

## 8. Documentação relacionada

| Documento | Conteúdo |
| --- | --- |
| `PRODUCT_SPEC.md` | O que é Blue, usuários, funcionalidades, fluxos, regras. |
| `DOMAIN_SPEC.md` | Entidades, campos, enums, cardinalidades, regras de reserva. |
| `API_SPEC.md` | Contratos propostos da API (CURRENT → PLANNED). |
| `ROADMAP.md` | Plano de implementação (fases 0–8). |
| `DECISIONS.md` | ADRs e decisões abertas (D1–D10). |

**Documentação existente do frontend** (preservada, não substituída):

| Documento | Propósito |
| --- | --- |
| `docs/README.md` | Visão geral do projeto e stack atual. |
| `docs/ai-context.md` | Contexto e directrizes de desenho do frontend (hero original, tokens, widget cardápio). |
| `docs/development-guide.md` | Guia de desenvolvimento frontend (npm, estrutura crítica, convenções). |
| `docs/project-map.md` | Mapa do projeto e fluxos atuais. |

> Fim de `ARCHITECTURE.md`.