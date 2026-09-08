# Blue — API Specification v1.0

> **Status:** `[PLANNED]` — especificação proposta para o backend. **Não existe ainda** nenhum endpoint (estado atual = dados client-side; ver `ARCHITECTURE.md`).
> **Fonte funcional:** [PRODUCT_SPEC.md](./PRODUCT_SPEC.md) e [DOMAIN_SPEC.md](./DOMAIN_SPEC.md).

## Convenções de estado

| Tag | Significado |
| --- | --- |
| `[PLANNED]` | Endpoint planejado, ainda não implementado. |
| `[DECISION]` | Comportamento definido. |
| `[TBD]` | Comportamento ainda aberto. |

## Índice

1. [Estado atual (CURRENT)](#1-estado-atual-current)
2. [Principios gerais](#2-principios-generais)
3. [Autenticação e autorização](#3-autenticação-e-autorização)
4. [Grupo /auth](#4-grupo-auth)
5. [Grupo /users](#5-grupo-users)
6. [Grupo /restaurants](#6-grupo-restaurants)
7. [Grupo /reservations](#7-grupo-reservations)
8. [Grupo /tables](#8-grupo-tables)
9. [Grupo /menu](#9-grupo-menu)
10. [Grupo /preorders](#10-grupo-preorders)
11. [Grupo /reviews](#11-grupo-reviews)
12. [Grupo /events](#12-grupo-events)
13. [Grupo /notifications](#13-grupo-notifications)
14. [Grupo /admin](#14-grupo-admin)

---

## 1. Estado atual (CURRENT)

```
CURRENT: NÃO EXISTE API.
```

O frontend atual funciona **sem backend**: dados simulados, estado em memória e `localStorage`. Nenhum endpoint abaixo existe hoje. Esta seção marca o estado `[CURRENT]` como **vazio** e toda a API como **`[PLANNED]`**.

## 2. Principios gerais

- Autenticação via **JWT bearer token** (access token sem refresh no MVP — ADR-014).
- `CUSTOMER` acessa **seus** recursos; `ADMIN` acessa recursos do restaurante e do painel.
- Erros padrão: `400` (validação/semântica), `401` (não autenticado), `403` (sem permissão), `404` (não encontrado), `409` (conflito de disponibilidade/duplicidade), `422` (formato).
- Formatos: data `YYYY-MM-DD`; horários `HH:MM` (24h); durações em minutos. (`[DECISION]`)
- Paginação `?limit&offset` para listagens (`[PROPOSTA]`).
- Reservas: duração e antecedência validadas contra `RestaurantSettings` (defaults — ADR-010); overlap por mesa → `409`; criação/alocação **transacional** (ADR-011).

## 3. Autenticação e autorização

| Aspecto | Valor |
| --- | --- |
| Header | `Authorization: Bearer <token>` |
| Roles | `CUSTOMER`, `ADMIN` |
| Restrição | Recursos do cliente filtrados por `user_id` do token; recursos admin exigem role `ADMIN`. |

---

## 4. Grupo /auth

### `POST /auth/register` — Cadastro de cliente

- **Auth:** pública `[DECISION]`.
- **Role:** — (pública; cria `CUSTOMER`).
- **Request:**
  ```json
  { "name": "string", "email": "string", "password": "string", "phone": "string?" }
  ```
- **Response:** `201` — `{ "user": {...}, "token": "..." }`
- **Erros:** `409` (e-mail já registrado), `422`, `400`.
- **Finalidade:** criar conta de cliente e devolver sessão.

### `POST /auth/login` — Login

- **Auth:** — (pública).
- **Role:** —.
- **Request:** `{ "email": "string", "password": "string" }`
- **Response:** `200` — `{ "access_token": "...", "token_type": "bearer", "user": {...} }`
- **Erros:** `401` (credenciais inválidas), `422`.
- **Finalidade:** autenticar e obter token.

### `GET /auth/me` — Perfil da sessão

- **Auth:** sim `[DECISION]`.
- **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — `{ "user": {...} }`
- **Erros:** `401`.
- **Finalidade:** obter usuário autenticado (também valida a sessão).

---

## 5. Grupo /users

### `GET /users/me` — Dados do próprio usuário

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — dados do usuário (sem `password_hash`).
- **Erros:** `401`.
- **Finalidade:** consultar o próprio perfil.

### `PATCH /users/me` — Atualizar perfil

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Request:** `{ "name"?: "string", "phone"?: "string", "email"?: "string" }`
- **Response:** `200` — dados atualizados.
- **Erros:** `401`, `409` (e-mail em uso), `422`.
- **Finalidade:** editar dados do próprio perfil.

> Não há endpoints para listar/gerir usuários pelo cliente; gestão de usuários admin `[TBD]` no MVP.

---

## 6. Grupo /restaurants

### `GET /restaurants` — Listar restaurantes

- **Auth:** sim (autenticado) ou pública `[TBD]`. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — `{ "items": [ { "id", "name", "slug", "phone", "description", "address", "is_active" } ], "limit", "offset", "total" }`
- **Erros:** `401`.
- **Finalidade:** listar restaurantes; no MVP tipicamente um.

### `GET /restaurants/{id}` — Detalhe

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — restaurante + settings resumidos.
- **Erros:** `404`.
- **Finalidade:** consultar o restaurante e configurações públicas.

### `GET /restaurants/{id}/settings` — Configurações públicas

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — `{ "min_duration_minutes", "max_duration_minutes", "duration_step_minutes", "min_people", "max_people", "cancellation_window_minutes", "min_booking_lead_minutes", "max_booking_lead_days", "preorder_enabled" }`
- **Erros:** `404`.
- **Finalidade:** o cliente conhece durações, antecedências e pessoas permitidas antes de criar/editar reservas (R4, ADR-010).

---

## 7. Grupo /reservations

### `GET /reservations/availability` — Disponibilidade

- **Auth:** sim. **Role:** `CUSTOMER`.
- **Query params:** `restaurant_id`, `date`, `start_time`, `duration_minutes` (opcional; default do restaurante), `people_count`.
- **Response:** `200` — `{ "status": "available" | "unavailable" | "partial", "conflicting_slots": [...], "estimated_tables": n }`
- **Erros:** `400`, `404`; `422` (duração fora de `[min,max]`/passo ou antecedência fora da janela — ADR-010).
- **Regras:** durações e antecedências validadas contra `RestaurantSettings` (ADR-010); mesas com slots adjacentes são consideradas disponíveis (ADR-011).
- **Finalidade:** pré-validar disponibilidade no fluxo de reserva (não reserva).

### `POST /reservations` — Criar reserva

- **Auth:** sim. **Role:** `CUSTOMER`.
- **Request:**
  ```json
  {
    "restaurant_id": "uuid",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "duration_minutes": 90,
    "people_count": 4,
    "notes": "string?"
  }
  ```
- **Response:** `201` — `{ "reservation": {...}, "allocated_tables": [ {mesas} ] }`
- **Erros:** `400/422`, `401`, `403`; `409` (overlap por mesa — ADR-011 — ou reserva simultânea do usuário — R15).
- **Validações (ADR-010):** `duration_minutes` entre os limites mínimo/máximo e múltiplo do passo; `start_time` ≥ antecedência mínima e ≤ antecedência máxima (defaults 1 h e 90 dias). Valores lidos de `RestaurantSettings`, nunca fixos.
- **Integridade (ADR-011):** criação + alocação de mesas em **transação única**, com bloqueio das mesas candidatas, evitando race conditions em reservas simultâneas.
- **Finalidade:** criar a reserva e devolver a alocação de mesas (ADR-004/005).

### `GET /reservations` — Listar (próprias)

- **Auth:** sim. **Role:** `CUSTOMER` (só suas) | `ADMIN` (todas, com query `user_id`/`date`).
- **Response:** `200` — `{ "items": [ { reserva + mesas + status } ], "limit", "offset", "total" }`
- **Erros:** `401`.

### `GET /reservations/{id}` — Detalhe

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário) | `ADMIN`.
- **Response:** `200` — reserva + mesas + estado + pré-pedido associado.
- **Erros:** `404`, `403`.

### `PATCH /reservations/{id}` — Editar

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário) | `ADMIN`.
- **Request:** campos editáveis: `date`, `start_time`, `duration_minutes`, `people_count`, `notes`.
- **Response:** `200` — reserva atualizada + re-alocação se necessário.
- **Erros:** `404/403`; `409` (disponibilidade/overlap após a mudança — ADR-011; estado não editável); `422` (duração/antecedência fora dos limites — ADR-010).
- **Integridade:** edição + re-alocação em **transação única**, revalidando duração/antecedência (ADR-010) e overlap por mesa (ADR-011).
- **Finalidade:** implementar o fluxo de alteração (§4.3 de `PRODUCT_SPEC.md`).

### `DELETE /reservations/{id}` — Cancelar (negocial)

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário) | `ADMIN`.
- **Request:** corpo opcional `{ "reason": "string?" }`.
- **Response:** `200` — `{ "reservation": { ..., "status": "CANCELLED", "cancelled_by": "...", "cancelled_at": "..." } }` — **não há exclusão física**; a reserva e as `ReservationTable` permanecem como histórico.
- **Erros:** `404/403`; `409` se a janela de cancelamento já passou (R14 — default 60 min antes do início, ADR-010) ou o estado não o permite.
- **Finalidade:** cancelamento negocial dentro da janela configurada (R12/R13), com rastreabilidade de quem/quando cancelou.

---

## 8. Grupo /tables

> As mesas são recursos do restaurante. A leitura pública consulta no contexto do restaurante; a gestão admin pode residir em `/admin/tables` ou directo em `/tables` (decisão de roteamento `[TBD]`).

### `GET /restaurants/{id}/tables` — Listar mesas (público)

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — `{ "items": [ { "id", "label", "capacity", "is_locked" } ] }` (clientes veem só `is_locked=false`; admin ve todas).
- **Erros:** `401`, `404`.
- **Finalidade:** o cliente ve capacidade disponível; o admin gerencia.

### `POST /tables` — Criar mesa (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** `{ "restaurant_id", "label", "capacity", "position_x"?, "position_y"?, "position_z"?, "is_locked"? }`
- **Response:** `201` — mesa criada.
- **Erros:** `400/422`, `403`.

### `PATCH /tables/{id}` — Atualizar mesa (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** campos editáveis: `label`, `capacity`, `position_*` (TBD), `is_locked` (bloqueio R8), `is_active`.
- **Response:** `200`.
- **Erros:** `403`, `404`, `409` se a mudança invalida reservas activas (detalhe `[TBD]`).

---

## 9. Grupo /menu

### `GET /restaurants/{id}/menu` — Cardápio público (referido como `GET /menu`)

- **Auth:** sim (possibilita acesso sem login `[TBD]`). **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — `{ "categories": [ { "id", "name", "sort_order", "items": [ { "id", "name", "description", "price", "image_url", "is_available", "is_review_eligible" } ] } ] }` (clientes veem só `is_available=true`).
- **Erros:** `404`.
- **Finalidade:** consumir o cardápio no widget atual do frontend; `is_review_eligible` alimenta a elegibilidade de avaliação de pratos (ADR-012).

### `POST /menu/categories` — Criar categoria (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** `{ "restaurant_id", "name", "sort_order"? }`
- **Response:** `201`.
- **Erros:** `400/422`, `403`.

### `PATCH /menu/categories/{id}` — Editar categoria (admin)

- **Auth:** sim. **Role:** `ADMIN`. **Response:** `200`. **Erros:** `403`, `404`.

### `POST /menu/items` — Criar item (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** `{ "category_id", "name", "description"?, "price", "image_url"?, "is_available"?, "is_review_eligible"? }`
- **Response:** `201`.
- **Erros:** `400/422`, `403`, `404` (categoria).

### `PATCH /menu/items/{id}` — Editar item (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** campos editáveis: `name`, `description`, `price`, `image_url`, `is_available`, `is_review_eligible`, `category_id`.
- **Response:** `200`.
- **Erros:** `403`, `404`.

> Eliminação de categorias/items (DELETE físico vs `is_active=false`) — `[TBD]`.

---

## 10. Grupo /preorders

### `POST /preorders` — Criar pré-pedido

- **Auth:** sim. **Role:** `CUSTOMER`.
- **Request:** `{ "reservation_id", "items": [ { "menu_item_id", "quantity" } ], "notes"? }`
- **Response:** `201` — `{ "pre_order": {...}, "items": [...] }`
- **Erros:** `400/422`, `403` (reserva não é do usuário), `404` (reserva), `409` (pré-pedido ativo existente — D1; reserva não `CONFIRMED`).
- **Finalidade:** crear pré-pedido (estado `DRAFT` → depois `SUBMITTED`).

### `POST /preorders/{id}/submit` — Enviar pré-pedido

- **Auth:** sim. **Role:** `CUSTOMER`.
- **Response:** `200` — `{ "pre_order": { ..., "status": "SUBMITTED" } }`
- **Erros:** `403/404`, `409` (estado inválido).
- **Finalidade:** passar de `DRAFT` a `SUBMITTED`.

### `PATCH /preorders/{id}` — Editar pré-pedido

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário) | `ADMIN`.
- **Request:** `{ "items"?: [ { "menu_item_id", "quantity" } ], "notes"?: "string" }` (somente em `DRAFT`/`SUBMITTED`).
- **Response:** `200` — `{ "pre_order": {...}, "items": [...] }`.
- **Erros:** `403/404`, `409` (estado não permite mudanças; reserva não `CONFIRMED`).
- **Finalidade:** alterar pré-pedido dentro das regras (R19); limites exatos — D1 `[TBD]`.

### `POST /preorders/{id}/cancel` — Cancelar pré-pedido

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — status `CANCELLED`.
- **Erros:** `403/404`, `409`.

### `GET /preorders/{id}` — Detalhe

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário) | `ADMIN`.
- **Response:** `200` — pré-pedido + items + status.
- **Erros:** `403/404`.

---

## 11. Grupo /reviews

> Regras fechadas em ADR-012 (D5): uma avaliação de restaurante por reserva concluída; apenas pratos elegíveis do pré-pedido da experiência; cada prato uma única vez por avaliação; **sem edição** da avaliação no MVP.

### `POST /reviews` — Avaliar restaurante + pratos

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário da reserva).
- **Request:**
  ```json
  {
    "reservation_id": "uuid",
    "rating": 4,
    "comment": "string",
    "items": [ { "menu_item_id": "uuid", "rating": 5 } ]
  }
  ```
- **Response:** `201` — `{ "review": {...}, "items": [...] }`
- **Erros:** `400/422` (nota fora de 1–5; item duplicado em `items`), `403` (reserva não é do usuário / reserva não `COMPLETED`), `404` (reserva/item), `409` (reserva já avaliada — ADR-012 — ou item não elegível).
- **Regras:** reserva deve estar `COMPLETED` (ADR-007); elegibilidade dos `items` validada contra o pré-pedido da reserva; cada prato avaliado uma única vez por avaliação; **sem edição** posterior da avaliação (ADR-012).
- **Finalidade:** criar a avaliação única da experiência (ADR-007/012).

### `GET /restaurants/{id}/reviews` — Listar avaliações publicadas

- **Auth:** no (público) ou sim `[TBD]`. **Role:** — (público).
- **Response:** `200` — `{ "items": [ { "id", "rating", "comment", "customer_name", "created_at", "admin_response", "items": [...] } ], "summary": { "avg_rating", "total" } }`
- **Erros:** `404`.
- **Finalidade:** mostrar as avaliações publicadas no frontend atual.

### `POST /reviews/{id}/response` — Responder avaliação (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** `{ "admin_response": "string" }`
- **Response:** `200`.
- **Erros:** `403`, `404`.

### `PATCH /reviews/{id}/moderation` — Moderar (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** `{ "status": "PUBLISHED" | "HIDDEN" }`
- **Response:** `200`.
- **Erros:** `403`, `404`, `422`.

---

## 12. Grupo /events

### `POST /event-requests` — Solicitar evento

- **Auth:** sim. **Role:** `CUSTOMER`.
- **Request:** `{ "restaurant_id", "contact_name", "contact_phone"?, "event_date", "people_count"?, "description"? }`
- **Response:** `201` — `{ "event_request": { ..., "status": "PENDING" } }`
- **Erros:** `400/422`, `401`.
- **Finalidade:** criar a solicitação em `PENDING`.

### `GET /event-requests` — Listar (próprias)

- **Auth:** sim. **Role:** `CUSTOMER` (só suas) | `ADMIN` (todas).
- **Response:** `200`.

### `POST /event-requests/{id}/cancel` — Cancelar

- **Auth:** sim. **Role:** `CUSTOMER` (proprietário).
- **Response:** `200` — status `CANCELLED`.
- **Erros:** `403/404`, `409`.

### `PATCH /event-requests/{id}` — Aprovar/Rejeitar (admin)

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** `{ "status": "APPROVED" | "REJECTED", "admin_notes"? }`
- **Response:** `200`.
- **Erros:** `403`, `404`, `409` (transição inválida).

---

## 13. Grupo /notifications

### `GET /notifications` — Listar notificações

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Query:** `?unread_only=true&limit&offset`.
- **Response:** `200` — `{ "items": [ { "id", "type", "title", "body", "is_read", "created_at" } ], "unread_count" }`
- **Erros:** `401`.
- **Finalidade:** alimentar o centro de notificações (ADR-008; inicialmente polling).

### `PATCH /notifications/read-all` — Marcar todas como lidas

- **Auth:** sim. **Role:** `CUSTOMER` | `ADMIN`.
- **Response:** `200` — `{ "updated": n }`.

### `DELETE /notifications/{id}` — Remover uma

- **Auth:** sim. **Role:** proprietário | `ADMIN`.
- **Response:** `204`.
- **Erros:** `403/404`.

---

## 14. Grupo /admin

> Endpoints de gestão (role `ADMIN`). Agrupados sob `/admin` para o painel; os recursos de domínio mantêm role-check nos seus módulos (ver nota final).

### `GET /admin/dashboard` — Resumo operativo

- **Auth:** sim. **Role:** `ADMIN`.
- **Response:** `200` — `{ "today_reservations", "pending_reviews", "pending_events", "active_tables" }` (conteúdo `[TBD]`).
- **Finalidade:** vista inicial do painel admin.

### `PATCH /admin/restaurants/{id}/settings` — Editar configuração

- **Auth:** sim. **Role:** `ADMIN`.
- **Request:** campos editáveis de `RestaurantSettings` (`cancellation_window_minutes`, `min_booking_lead_minutes`, `max_booking_lead_days`, limites de duração/pessoas, `preorder_enabled`, …).
- **Response:** `200`.
- **Erros:** `403`, `404`, `422`.

### `POST /admin/capacity-rules` — Criar regra de capacidade

- **Auth:** sim. **Role:** `ADMIN`. **Request:** `{ "restaurant_id", "min_people", "max_people", "tables_required" }` → `201`.
- **Erros:** `422` (faixa sobreposta), `403`.

### `PATCH /admin/capacity-rules/{id}` — Editar/habilitar regra

- **Auth:** sim. **Role:** `ADMIN`. **Response:** `200`.

### `GET /admin/reservations` — Listar reservas (admin)

- **Auth:** sim. **Role:** `ADMIN`. **Query:** `date`, `status`, `user_id`?, `limit`, `offset`. → `200`.

### `PATCH /admin/reservations/{id}/status` — Cambiar estado

- **Auth:** sim. **Role:** `ADMIN`. **Request:** `{ "status": "CONFIRMED" | "COMPLETED" | "NO_SHOW" | "CANCELLED" }` → `200`.
- **Erros:** `409` (transição inválida), `404`.

---

> **Nota final:** a agrupação `/admin` é organizacional; a autorização (role `ADMIN`) aplica-se em cada módulo de domínio. Decisão de roteamento final `[TBD]`.

> Fim de `API_SPEC.md`. Toda a seção é `[PLANNED]`; não existe ainda nenhum endpoint (`CURRENT`: vazio).