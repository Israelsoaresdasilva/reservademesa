# Blue — Domain Specification v1.0

> **Status:** `[DECISION]` para a identidade das entidades e enums; campos marcados `[TBD]` ou `[PROPOSTA]` ainda não estão fechados.
> **Propósito:** descrever formalmente o domínio do Blue para o desenvolvimento do backend (Python/FastAPI/PostgreSQL).
> **Documentos:** ver [PRODUCT_SPEC.md](./PRODUCT_SPEC.md) (regras de negócio em linguagem de produto) e [DECISIONS.md](./DECISIONS.md) (decisões de arquitetura).

## Convenções

| Tag | Significado |
| --- | --- |
| `[DECISION]` | Modelo/regra definida. |
| `[PROPOSTA]` | Proposta inicial que ainda não foi confirmada. |
| `[TBD]` | Campo/relação ainda não definido. |
| `PK` | Chave primária. |
| `FK` | Chave estrangeira. |
| audit | `created_at`/`updated_at` (UTC) seguem o mesmo padrão em todas as entidades. |

## Índice

- [1. Visão geral](#1-visão-geral)
- [2. Entidades](#2-entidades)
- [3. Relacionamentos e cardinalidades](#3-relacionamentos-e-cardinalidades)
- [4. Enums](#4-enums)
- [5. Regras de reserva](#5-regras-de-reserva)

---

## 1. Visão geral

O domínio do Blue é composto por:

- **Identidade e acesso:** `User`, `Notification`.
- **Restaurante:** `Restaurant`, `RestaurantSettings`, `Table`, `CapacityRule`.
- **Operação de salão:** `Reservation`, `ReservationTable` (junção N:N).
- **Venda e experiências:** `MenuCategory`, `MenuItem`, `PreOrder`, `PreOrderItem`.
- **Retorno e análise:** `Review`, `ReviewItem`.
- **Eventos:** `EventRequest`.

Regras gerais:

- Toda entidade com dados mutáveis carrega `created_at` e `updated_at` (`[PROPOSTA]` — mesmo padrão em todas).
- Entidades de linha (`PreOrderItem`, `ReviewItem`) são **append-only**: registram apenas `created_at`, sem `updated_at` (ADR-012).
- IDs são UUID (`[PROPOSTA]` — pode ser revisado na implementação).
- Valores monetários são `numeric` (evitar float) (`[PROPOSTA]`).

---

## 2. Entidades

> Formato por entidade: **Finalidade** · **Campos** · **Relacionamentos** · **Regras**.
> Obrigatoriedade: ✅ obrigatório, ⭕ opcional, `[TBD]` ainda não definido.

### 2.1 User

**Finalidade:** identidade digital do cliente e do staff interno (admin).

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| name | string | ✅ | Nome visível. |
| email | string | ✅ | E-mail único de acesso (login). |
| phone | string | ⭕ | Telefone de contato. |
| password_hash | string | ✅ | Hash da senha (nunca em claro). |
| role | enum(`UserRole`) | ✅ | `CUSTOMER` ou `ADMIN`. |
| is_active | boolean | ✅ | Desativa o acesso (default `true`). |
| created_at | datetime | ✅ | Auditoria. |
| updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** 1:N `Reservation`, 1:N `Review`, 1:N `EventRequest`, 1:N `Notification`.

**Regras:** e-mail único; `role` restrito a `CUSTOMER`/`ADMIN` (ADR-009); senha somente como hash.

### 2.2 Restaurant

**Finalidade:** representar o restaurante (marca de referência "Ocean Blue") no sistema.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| name | string | ✅ | Nome do restaurante. |
| slug | string | ⭕ | Identificador para URLs (único se usado). |
| phone | string | ⭕ | Telefone de contato. |
| description | text | ⭕ | Descrição pública. |
| address | string | ⭕ | Endereço. |
| is_active | boolean | ✅ | Habilita/desabilita operação (default `true`). |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** 1:1 `RestaurantSettings`, 1:N `Table`, 1:N `CapacityRule`, 1:N `Reservation`, 1:N `MenuCategory`, 1:N `Review`, 1:N `EventRequest`.

**Regras:** o MVP opera **um** restaurante por instância (D3 `[TBD]`); o modelo já suporta N.

### 2.3 RestaurantSettings

**Finalidade:** configuração operacional do restaurante que afeta as regras de reserva.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| restaurant_id | FK → Restaurant | ✅ | Único (1:1 com restaurante). |
| cancellation_window_minutes | int | ✅ | Cancelamento permitido até X minutos antes do início (default `60` = 1 hora — ADR-010). |
| min_booking_lead_minutes | int | ✅ | Antecedência mínima para criar/editar reserva, em minutos antes do início (default `60` = 1 hora — ADR-010). |
| max_booking_lead_days | int | ✅ | Antecedência máxima para reservar, em dias (default `90` — ADR-010). |
| max_people_per_reservation | int | ✅ | Máximo de pessoas por reserva. |
| min_people_per_reservation | int | ✅ | Mínimo de pessoas por reserva (default proposto `[PROPOSTA]`). |
| reservation_min_duration_minutes | int | ✅ | Duração mínima oferecida (default `30` — ADR-010). |
| reservation_max_duration_minutes | int | ✅ | Duração máxima oferecida (default `180` = 3 horas — ADR-010). |
| reservation_duration_step_minutes | int | ✅ | Passo entre durações permitidas (default `30` — ADR-010). |
| preorder_enabled | boolean | ✅ | Habilita pré-pedidos (default `true`). |
| review_allowed_after_hours | int | `[TBD]` | Tempo mínimo após a reserva para poder avaliar. |
| opening_hours | json | `[TBD]` | Janelas de horário operativo (D10). |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `Restaurant` (1:1 lógico).

**Regras:** faixa de duração válida (min ≤ step ≤ max); janela de cancelamento positiva; antecedência mínima < antecedência máxima; os defaults (ADR-010) são valores de configuração aplicados pelo service — **não** são constantes do domínio e podem ser alterados pelo ADMIN.

### 2.4 Table

**Finalidade:** mesa física do salão, alocável a uma reserva.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| restaurant_id | FK → Restaurant | ✅ | Restaurante proprietário. |
| label | string | ✅ | Rótulo/mesa (ex.: "12"). |
| capacity | int | ✅ | Capacidade de pessoas (≥ 1). |
| is_locked | boolean | ✅ | Bloqueada pelo admin (excluída da alocação). |
| position_x / position_y / position_z | float | ⭕ | Posição no mapa 3D (`[PROPOSTA]` — persistência da calibração `[TBD]`). |
| is_active | boolean | ✅ | Ativa (default `true`). |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `Restaurant`; N:N `Reservation` via `ReservationTable` (ADR-004).

**Regras:** `capacity > 0`; `is_locked = true` exclui a mesa da alocação automática (R8).

---

### 2.5 CapacityRule

**Finalidade:** definir quantas mesas são necessárias para uma faixa de pessoas (alocação automática, ADR-005).

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| restaurant_id | FK → Restaurant | ✅ | Restaurante proprietário. |
| min_people | int | ✅ | De X pessoas (inclusivo). |
| max_people | int | ✅ | Até X pessoas (inclusivo). |
| tables_required | int | ✅ | Número de mesas necessárias para a faixa. |
| is_active | boolean | ✅ | Regra ativa (default `true`). |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `Restaurant`.

**Regras:** faixas sem sobreposição entre si (para um restaurante); `min_people <= max_people`; `tables_required >= 1`. A regra cuja faixa contém `people_count` define o número de mesas. Detalhes (combinações por capacidade residual) `[TBD]` — não é o D4 (já fechado em ADR-011 como regra de overlap).

### 2.6 Reservation

**Finalidade:** núcleo do produto — reserva de uma experiência no restaurante.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| user_id | FK → User | ✅ | Cliente que reserva. |
| restaurant_id | FK → Restaurant | ✅ | Restaurante. |
| date | date | ✅ | Data da reserva. |
| start_time | time | ✅ | Horário de início (`HH:MM`). |
| duration_minutes | int | ✅ | Duração escolhida (dentro dos limites configurados, R4). |
| people_count | int | ✅ | Quantidade de pessoas (R5). |
| status | enum(`ReservationStatus`) | ✅ | Ver §4.2. |
| notes | text | ⭕ | Notas do cliente. |
| cancelled_by | enum(`UserRole`) | ⭕ | Quem cancelou (`CUSTOMER`/`ADMIN`); preenchido no cancelamento. |
| cancelled_at | datetime | ⭕ | Data/hora do cancelamento; preenchido no cancelamento. |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `User`, N:1 `Restaurant`, N:N `Table` via `ReservationTable` (ADR-004); 0..1 `Review` (uma avaliação de restaurante por reserva — ADR-012); 0..1 `PreOrder` (D1 aberto).

**Regras:** ver regras R1–R15 em `PRODUCT_SPEC.md` §5; duração e antecedência validadas contra `RestaurantSettings` (ADR-010); cancelamento somente dentro da janela configurada (R14); anti-overlap por mesa §5.1 (ADR-011).

### 2.7 ReservationTable

**Finalidade:** associação reserva ↔ mesas (resultado da alocação).

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| reservation_id | FK → Reservation | ✅ | Reserva. |
| table_id | FK → Table | ✅ | Mesa alocada. |
| allocated_at | datetime | ✅ | Momento da alocação. |

**Relacionamentos:** N:1 `Reservation`, N:1 `Table`.

**Regras:** único por par `(reservation_id, table_id)`; somente mesas livres e não bloqueadas são alocadas; a criação/alocação (e a re-alocação em edição) é **transacional** e valida overlap por mesa (ADR-011).

### 2.8 MenuCategory

**Finalidade:** agrupamento do cardápio (ex.: "PRATOS", "BEBIDAS").

 

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| restaurant_id | FK → Restaurant | ✅ | Restaurante. |
| name | string | ✅ | Nome da categoria. |
| sort_order | int | ✅ | Ordem de exibição (default 0). |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `Restaurant`, 1:N `MenuItem`.

### 2.9 MenuItem

**Finalidade:** prato/bebida do cardápio.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| category_id | FK → MenuCategory | ✅ | Categoria. |
| name | string | ✅ | Nome. |
| description | text | ⭕ | Descrição. |
| price | numeric(10,2) | ✅ | Preço. |
| image_url | string | ⭕ | Imagem. |
| is_available | boolean | ✅ | Disponível/aparece publicado (default `true`). |
| is_review_eligible | boolean | ✅ | Elegível para avaliação de prato (alinhado com ADR-007). |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `MenuCategory`, 1:N `PreOrderItem`, 1:N `ReviewItem`.

**Regras:** preço > 0; `is_available = false` oculta o item do público. A elegibilidade efetiva de um prato depende do pré-pedido associado à reserva (ADR-007).

---

### 2.10 PreOrder

**Finalidade:** pré-pedido vinculado a uma reserva (ADR-006 — separado de pagamento).



| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| reservation_id | FK → Reservation | ✅ | Reserva associada (único ativo por reserva — D1 `[TBD]`). |
| status | enum(`PreOrderStatus`) | ✅ | Ver §4.3. |
| notes | text | ⭕ | Notas do cliente. |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `Reservation` (1:1 ativo), 1:N `PreOrderItem`.

**Regras:** somente um pré-pedido ativo por reserva `[TBD]` (D1); transições de estado segundo §4.3.

### 2.11 PreOrderItem

**Finalidade:** linha do pré-pedido (item + quantidade.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| pre_order_id | FK → PreOrder | ✅ | Pré-pedido. |
| menu_item_id | FK → MenuItem | ✅ | Item do cardápio. |
| quantity | int | ✅ | Quantidade (> 0). |
| unit_price_snapshot | numeric(10,2) | ⭕ | Preço no momento do pré-pedido (`[PROPOSTA]`). |
| notes | text | ⭕ | Notas. |
| created_at | datetime | ✅ | Auditoria (linha append-only; sem `updated_at`). |

**Relacionamentos:** N:1 `PreOrder`, N:1 `MenuItem`.

**Regras:** `quantity > 0`; restrição de disponibilidade do item defendida no service.

### 2.12 Review

**Finalidade:** avaliação do restaurante vinculada a uma experiência/reserva concluída (ADR-007).

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| reservation_id | FK → Reservation | ✅ | Reserva concluída avaliada (uma por reserva — ADR-012). |
| user_id | FK → User | ✅ | Autor. |
| restaurant_id | FK → Restaurant | ✅ | Restaurante. |
| rating | int | ✅ | Nota geral 1–5. |
| comment | text | ✅ | Texto. |
| status | enum(`ReviewStatus`) | ✅ | `PUBLISHED` / `HIDDEN` (moderação). |
| admin_response | text | ⭕ | Resposta do admin (texto). |
| responded_at | datetime | ⭕ | Data da resposta; preenchido junto com `admin_response`. |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** 1:1 `Reservation` (uma avaliação de restaurante por reserva — ADR-012), N:1 `User`, N:1 `Restaurant`, 1:N `ReviewItem`.

**Regras:** somente após reserva `COMPLETED` (ADR-007); **uma** avaliação de restaurante por reserva — constraint única em `reservation_id` (ADR-012); **sem edição** da avaliação no MVP (ADR-012); admin modera (`PUBLISHED`/`HIDDEN`) e responde.

### 2.13 ReviewItem

**Finalidade:** avaliação de um prato específico, elegível via pré-pedido da experiência.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| review_id | FK → Review | ✅ | Avaliação pai. |
| menu_item_id | FK → MenuItem | ✅ | Prato avaliado. |
| rating | int | ✅ | Nota 1–5. |
| created_at | datetime | ✅ | Auditoria (linha append-only; sem `updated_at`). |

**Relacionamentos:** N:1 `Review`, N:1 `MenuItem`.

**Regras:** prato elegível somente se presente no pré-pedido da reserva da avaliação (ADR-007); cada prato avaliado **uma única vez** por avaliação — `UNIQUE(review_id, menu_item_id)` (ADR-012).

### 2.14 EventRequest

**Finalidade:** solicitação de evento no restaurante (aniversários, corporativos, etc.).

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| user_id | FK → User | ✅ | Solicitante (cliente). |
| restaurant_id | FK → Restaurant | ✅ | Restaurante. |
| contact_name | string | ✅ | Nome de contato (pode ser o do usuário). |
| contact_phone | string | ⭕ | Telefone de contato. |
| event_date | date | ✅ | Data do evento. |
| people_count | int | ⭕ | Estimativa de convidados. |
| description | text | ⭕ | Descrição/tipo de evento. |
| status | enum(`EventRequestStatus`) | ✅ | Ver §4.4. |
| admin_notes | text | `[TBD]` | Notas internas do admin. |
| created_at / updated_at | datetime | ✅ | Auditoria. |

**Relacionamentos:** N:1 `User`, N:1 `Restaurant`.

**Regras:** transições `PENDING` → `APPROVED`/`REJECTED` (admin), `CANCELLED` (cliente).

### 2.15 Notification

**Finalidade:** avisos in-app ao usuário (ADR-008).

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| id | UUID | ✅ | Identificador único. |
| user_id | FK → User | ✅ | Destinatário. |
| type | enum | ✅ | `info` / `success` / `error` (+ tipos de domínio `[TBD]`). |
| title | string | ✅ | Título. |
| body | text | ✅ | Mensagem. |
| is_read | boolean | ✅ | Lida (default `false`). |
| created_at | datetime | ✅ | Auditoria. |
| updated_at | datetime | ✅ | Auditoria (`is_read` é mutável). |

**Relacionamentos:** N:1 `User`.

**Regras:** máx. N notificações vigentes por usuário (`[TBD]` — hoje o frontend guarda 20); origem: eventos de domínio.

---

## 3. Relacionamentos e cardinalidades

> ✅ = decisão tomada; ⚠️ = aberta / precisa explicação.

| Relação | Cardinalidade | Estado |
| --- | --- | --- |
| `User` → `Reservation` | 1 : N | ✅ |
| `User` → `Review` | 1 : N | ✅ |
| `User` → `EventRequest` | 1 : N | ✅ |
| `User` → `Notification` | 1 : N | ✅ |
| `Restaurant` → `RestaurantSettings` | 1 : 1 | ✅ |
| `Restaurant` → `Table` | 1 : N | ✅ |
| `Restaurant` → `CapacityRule` | 1 : N | ✅ |
| `Restaurant` → `Reservation` | 1 : N | ✅ |
| `Restaurant` → `MenuCategory` | 1 : N | ✅ |
| `Restaurant` → `Review` | 1 : N | ✅ |
| `Restaurant` → `EventRequest` | 1 : N | ✅ |
| `Reservation` → `Table` | N : N via `ReservationTable` | ✅ (ADR-004) |
| `MenuCategory` → `MenuItem` | 1 : N | ✅ |
| `MenuItem` → `PreOrderItem` | 1 : N | ✅ |
| `PreOrder` → `PreOrderItem` | 1 : N | ✅ |
| `Reservation` → `PreOrder` | 1 : 1 ou 1 : N | ⚠️ **D1 aberta** |
| `Reservation` → `Review` | 0..1 : 1 — uma avaliação de restaurante por reserva (`UNIQUE reservation_id`) | ✅ (ADR-012) |
| `Review` → `ReviewItem` | 1 : N — cada prato uma única vez por avaliação (`UNIQUE review_id, menu_item_id`) | ✅ (ADR-012) |
| `MenuItem` → `ReviewItem` | 1 : N | ✅ |

### Notas sobre cardinalidades abertas (⚠️)

- **`Reservation` → `PreOrder` (D1):** o negócio pede "um pré-pedido por reserva". O modelo 1:N (com exclusão de mais de um ativo) é flexível e seguro; a forma exata (1:1 estricto vs 1:N com um ativo) deve ser decidida em D1. Não assumir uma exclusividade que a configuração do restaurante possa desmentir.
- ~~`Reservation` → `Review` (D5):~~ **resolvido em ADR-012** — uma avaliação de restaurante por reserva, garantida por constraint única em `Review.reservation_id` (0..1 por reserva).

---

## 4. Enums

### 4.1 UserRole — ✅ confirmado

| Valor | Significado |
| --- | --- |
| `CUSTOMER` | Cliente final. |
| `ADMIN` | Equipe interna / gestor. |

> Proposta: o enum reside em `app/modules/users/` e se reutiliza nos demais módulos que o necessitem.

### 4.2 ReservationStatus — ✅ confirmado

| Valor | Significado |
| --- | --- |
| `PENDING` | Criada, pendente de confirmação. |
| `CONFIRMED` | Confirmada (mesas alocadas). |
| `CANCELLED` | Cancelada (cliente o admin). |
| `COMPLETED` | Experiencia realizada. |
| `NO_SHOW` | Não compareceu. |

> Transições típicas: `PENDING` → `CONFIRMED` → `COMPLETED` | `NO_SHOW`; `PENDING`/`CONFIRMED` → `CANCELLED`. Quando exatamente se marca `COMPLETED`/`NO_SHOW` (por admin após o horário) — `[TBD]`.

### 4.3 PreOrderStatus — ✅ confirmado

| Valor | Significado |
| --- | --- |
| `DRAFT` | Em edição pelo cliente. |
| `SUBMITTED` | Enviado ao restaurante. |
| `CONFIRMED` | Aceito/confirmado. |
| `CANCELLED` | Cancelado dentro das regras. |

### 4.4 EventRequestStatus — ✅ confirmado

| Valor | Significado |
| --- | --- |
| `PENDING` | Esperando análise do admin. |
| `APPROVED` | Aprovado. |
| `REJECTED` | Rejeitado. |
| `CANCELLED` | Cancelado pelo cliente. |

### 4.5 ReviewStatus — ✅ confirmado

| Valor | Significado |
| --- | --- |
| `PUBLISHED` | Visível publicamente. |
| `HIDDEN` | Oculta (moderação). |

---

## 5. Regras de reserva (críticas)

### 5.1 Overlap

Uma mesma **mesa física** não pode estar associada a duas reservas cujos intervalos de tempo se sobreponham (D4 — ADR-011). Intervalo = `[start_time, start_time + duration_minutes)`; há sobreposição se `start_A < end_B` **e** `start_B < end_A`:

```
19:00 → 21:00   [ocupa a mesa]
21:00 → 23:00   [adjacente → PERMITIDO na mesma mesa — sem buffer no MVP]
20:00 → 22:00   [sobrepõe → INVÁLIDO na mesma mesa]
```

- A unidade de conflito é a **mesa física** (`ReservationTable`), não a "capacidade total" nem o cliente.
- **Sem buffer inter-slot no MVP** (D4 — ADR-011); margem de limpeza entre slots pode ser adicionada futuramente como configuração (`[FUTURE]`).
- A validação ocorre no **backend** e a criação/alocação da reserva (e a re-alocação em edição) é **transacional**: uma única transação com bloqueio das mesas candidatas (`SELECT ... FOR UPDATE`) e/ou constraint de exclusão no PostgreSQL, evitando race conditions em reservas simultâneas (ADR-005/011).

### 5.2 Capacidade

```
quantidade de pessoas
        ↓
CapacityRule             (faixa de pessoas → nº de mesas)
        ↓
número de mesas necessário
        ↓
mesas disponíveis         (não bloqueadas, sem conflito no horário)
        ↓
alocação                 (ReservationTable)
```

- O sistema **não modela** combinações físicas fixas de mesas no MVP (`[DECISION]`, ADR-005).
- O admin define as regras de capacidade (`CapacityRule`).
- Mesas bloqueadas (`is_locked`) não participam na alocação (R8).

---

> Fim de `DOMAIN_SPEC.md`. Campos `[TBD]`/`[PROPOSTA]` remanescentes serão fechados nas decisões ainda abertas — D1, D3, D6, D9, D10, D11 (ver `DECISIONS.md`).