# Blue — Product Specification v1.0

> **Status:** `[DECISION]` — fonte de verdade de produto do Blue v1 (MVP).
> **Produto:** Blue — sistema de reservas, cardápio, pré-pedidos, avaliações e eventos para restaurante.

> **Marca de referência:** "Ocean Blue" — restaurante de exemplo presente no frontend atual.

> **Documentos relacionados:** [DOMAIN_SPEC.md](./DOMAIN_SPEC.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [API_SPEC.md](./API_SPEC.md), [ROADMAP.md](./ROADMAP.md), [DECISIONS.md](./DECISIONS.md).

## Convenções de estado

| Tag | Significado |
| --- | --- |
| `[CURRENT]` | Já existe no frontend atual. |
| `[PLANNED]` | Planejado (backend/MVP), ainda não existe. |
| `[DECISION]` | Decisão de produto/arquitetura já tomada (ver `DECISIONS.md`). |
| `[TBD]` | Decisão aberta / ainda não definida. |
| `[FUTURE]` | Fora do escopo do MVP, possibilidade futura. |

## Índice

- [1. Visão do produto](#1-visão-do-produto)
- [2. Usuários](#2-usuários)
- [3. Funcionalidades do MVP](#3-funcionalidades-do-mvp)
- [4. Fluxos principais](#4-fluxos-principais)
- [5. Regras importantes](#5-regras-importantes)

---

## 1. Visão do produto

O **Blue** é um sistema web que concentra, em um único produto, o ciclo completo da experiência de um restaurante:

1. **Descoberta** — conhecer o restaurante e consultar o cardápio.
2. **Reserva** — escolher data, horário, duração (dentro de limites configurados) e quantidade de pessoas; o sistema valida a disponibilidade, aloca mesas dinamicamente e confirma.
3. **Pré-pedido** — a partir da reserva, o cliente seleciona pratos do cardápio e pode alterar/cancelar dentro das regras.
4. **Pós-experiência** — avaliações do restaurante e de pratos elegíveis, moderadas e respondidas pelo administrador.
5. **Notificações** — o cliente acompanha o ciclo por notificações in-app.

O produto também dá ao **administrador** o controle operacional do restaurante: mesas, regras de capacidade, janela de cancelamento, cardápio, reservas, avaliações e solicitações de eventos — tudo em um único painel.

**Escopo do MVP (resumo):** autenticação, reservas com alocação dinâmica de mesas, mesas e regras de capacidade, cardápio, pré-pedidos, avaliações, eventos e notificações in-app. **Pagamento e delivery NÃO fazem parte do MVP.**

> **Consistência com o estado atual:** o frontend atual simula parte dessas experiências com dados client-side (`[CURRENT]`). Nada do que está marcado como `[PLANNED]` existe ainda no backend. Ver `ARCHITECTURE.md` para a distinção explícita.



---

## 2. Usuários

### Cliente

- `[DECISION]` Possui conta no sistema.
- `[DECISION]` Pode fazer reservas (data, horário, duração e quantidade de pessoas).
- `[DECISION]` Pode consultar o cardápio do restaurante.
- `[DECISION]` Pode realizar pré-pedido a partir de uma reserva.
- `[DECISION]` Pode cancelar/editar a própria reserva dentro das regras configuradas pelo restaurante.
- `[DECISION]` Pode avaliar o restaurante e pratos elegíveis após a reserva concluída.
- `[DECISION]` Recebe notificações (in-app).

> No frontend atual não há conta — a reserva usa apenas CPF + nome (`[CURRENT]`). Com o backend, o cliente terá conta (`[PLANNED]`, ver §4.1).

### Administrador

- Usuário interno do restaurante.
- `[DECISION]` Gerencia o restaurante (identidade, dados gerais e configurações).
- `[DECISION]` Gerencia mesas (cadastro, edição, bloqueio).
- `[DECISION]` Gerencia regras de reserva (capacidade, janela de cancelamento, antecedência mínima/máxima, limites de duração/pessoas).
- `[DECISION]` Gerencia o cardápio (categorias, itens, disponibilidade).
- `[DECISION]` Gerencia reservas (visualizar, confirmar, cancelar).
- `[DECISION]` Modera avaliações (publicar/ocultar).
- `[DECISION]` Responde avaliações.
- `[DECISION]` Gerencia solicitações de eventos (aprovar/rejeitar).

### Perfis (roles)

| Perfil | Descrição |
| --- | --- |
| `CUSTOMER` | Cliente final do restaurante. |
| `ADMIN` | Usuário interno (staff do restaurante). |

- `[DECISION]` No MVP existem **somente** `CUSTOMER` e `ADMIN` (ver ADR-009).
- `[TBD]` Nenhum outro nível de perfil será criado no MVP; novos perfis seriam decisão futura.

---

## 3. Funcionalidades do MVP

> Para cada funcionalidade: descrição · ator · fluxo · regras · status (`MVP`, `Futuro`, `Não decidido`).

### 3.1 Authentication

- **Descrição:** cadastro e login do cliente; autenticação do administrador.
- **Ator:** `CUSTOMER`, `ADMIN`.
- **Fluxo:** cadastro (nome, e-mail, telefone opcional, senha) → login (e-mail + senha) → sessão/token → acesso ao sistema.
- **Regras:** e-mail único; senha armazenada somente como hash; criação do primeiro admin via seed (`[TBD]` — D6).
- **Status:** `MVP` | `[PLANNED]` (backend). `[CURRENT]` no frontend **não existe** (reserva com CPF, sem conta).

### 3.2 Reservations

- **Descrição:** criar, consultar, alterar e cancelar reservas, com alocação dinâmica de mesas.
- **Ator:** `CUSTOMER` (gerencia as próprias), `ADMIN` (gerencia todas).

- **Fluxo:** data → horário → duração → quantidade de pessoas → disponibilidade → alocação de mesas → confirmação.
- **Regras:** ver §5 (capacidade, overlap, janela de cancelamento, antecedência mínima/máxima, sem reservas simultâneas, etc.). Os valores padrão de duração/antecedência/cancelamento vivem em `RestaurantSettings` (ADR-010), não no domínio.
- **Status:** `MVP` | `[CURRENT]` parcial: frontend com seleção manual de mesas e data, sem horário/duração/pessoas (ver `ARCHITECTURE.md`).

### 3.3 Tables

- **Descrição:** mesas do salão com capacidade,posição opcional no mapa e bloqueio pelo admin.
- **Ator:** `ADMIN`.
- **Fluxo:** cadastro → configuração (capacidade, bloqueio) → uso na alocação automática.
- **Regras:** capacidade positiva; mesas bloqueadas ficam excluídas da alocação; uma reserva pode alocar múltiplas mesas.
- **Status:** `MVP` | `[CURRENT]` parcial: mapa 3D + calibração + `table-map.json` (dados de exemplo).

### 3.4 Menu

- **Descrição:** categorias e itens do cardápio com preço e disponibilidade.
- **Ator:** `ADMIN` (gerencia), `CUSTOMER` (consulta).
- **Fluxo:** admin cria categoria → cadastra ítem → define disponibilidade → cliente visualiza (widget).
- **Regras:** ítem pertence a uma categoria; preço obrigatório; ítem inativo não aparece publicado.
- **Status:** `MVP` | `[CURRENT]` parcial: array estático no frontend + `public/Cardápio.html` legado.

### 3.5 Pre-orders

- **Descrição:** pré-pedido vinculado a uma reserva, com itens e quantidades.
- **Ator:** `CUSTOMER`.
- **Fluxo:** reserva → visualizar cardápio → selecionar pratos → definir quantidades → enviar pré-pedido → alterar/cancelar dentro das regras.
- **Regras:** um único pré-pedido ativo por reserva (`[TBD]` — D1); alteração/cancelamento somente em estados permitidos.
- **Status:** `MVP` | `[PLANNED]` — não existe no frontend atual.

### 3.6 Reviews

- **Descrição:** avaliações do restaurante e de pratos elegíveis, com moderação e resposta do admin.
- **Ator:** `CUSTOMER` (publica), `ADMIN` (modera e responde).
- **Fluxo:** reserva concluída → cliente avalia o restaurante → avalia pratos elegíveis (vinculados ao pré-pedido da experiência) → admin modera/responde.
- **Regras:** somente após reserva concluída (`COMPLETED`, ADR-007); **uma** avaliação de restaurante por reserva (D5/ADR-012); prato elegível somente se associado ao pré-pedido da experiência; cada prato avaliado **uma única vez** por avaliação (D5/ADR-012); **sem edição** da avaliação no MVP (D5/ADR-012); admin modera (`PUBLISHED`/`HIDDEN`) e responde.
- **Status:** `MVP` | `[CURRENT]` parcial: tela com lista mockada e formulário em memória (sem persistência).

### 3.7 Events

- **Descrição:** solicitação de evento no restaurante com fluxo de análise pelo admin.
- **Ator:** `CUSTOMER` (solicita), `ADMIN` (analisa).
- **Fluxo:** cliente solicita → status `PENDING` → admin analisa → `APPROVED` / `REJECTED`; cliente pode cancelar (`CANCELLED`).
- **Regras:** campos mínimos (nome/contato, data, pessoas, descrição); `[TBD]` se evento bloqueia capacidade do salão (D10 relacionado).
- **Status:** `MVP` | `[CURRENT]` parcial: modal "Solicitar Evento" apenas com pop-up de confirmação, sem persistência.

### 3.8 Notifications

- **Descrição:** avisos ao cliente sobre o ciclo da experiência (reserva, pré-pedido, avaliação, evento, admin).
- **Ator:** sistema (emissor), `CUSTOMER` e `ADMIN` (receptores).
- **Fluxo:** evento de domínio → notificação in-app → centro de notificações (lida/não lida, limpar).
- **Regras:** iniciar somente `IN_APP` (ADR-008); e-mail `[FUTURE]`; sem push no MVP.
- **Status:** `MVP` | `[CURRENT]` parcial: provider em memória no frontend (limite 20 itens, types `success`/`error`/`info`).

### 3.9 Administration

- **Descrição:** área de gestão do restaurante (configurações, mesas, capacity rules, cardápio, reservas, avaliações, eventos).
- **Ator:** `ADMIN`.
- **Fluxo:** acesso autenticado com role `ADMIN` → painel por domínio.
- **Regras:** somente `ADMIN`; requer endpoints protegidos (grupo `/admin` e recursos com role check — ver `API_SPEC.md`).
- **Status:** `MVP` (mínimo) | `[PLANNED]` — não existe no frontend atual (sem área admin).

---

## 4. Fluxos principais

> Convenção: `→` indica o próximo passo. Estados marcados `[DECISION]` estão definidos; `[TBD]` indica decisão operativa pendente.

### 4.1 Cadastro / login

```
Cliente
→ cadastro (nome, e-mail, senha)     [DECISION]
→ login (e-mail + senha)              [DECISION]
→ acesso ao sistema (token)           [DECISION]
```

### 4.2 Reserva

```
Cliente
→ data                                [DECISION]
→ horário                             [DECISION]
→ antecedência mínima/máxima válidas  [DECISION — ADR-010]
→ quantidade de pessoas               [DECISION]
→ duração (defaults 30–180 min, passo 30) [DECISION — ADR-010]
→ disponibilidade (overlap por mesa)  [DECISION — ADR-011]
→ alocação de mesas (CapacityRule)    [DECISION — ADR-005]
→ confirmação                         [DECISION]
```

> No frontend atual a reserva NÃO inclui horário, duração nem quantidade de pessoas (`[CURRENT]` → `[PLANNED]`).

### 4.3 Alteração

```
Reserva existente
→ alterar data / horário / duração / pessoas
→ validar disponibilidade novamente
→ atualizar (re-alocação se necessário)    [DECISION — D2/D4: revalida duração/antecedência (ADR-010) e overlap por mesa (ADR-011), com re-alocação transacional]
```

### 4.4 Cancelamento

```
Cliente / Admin
→ solicitar cancelamento
→ verificar janela de cancelamento (default 1 h — ADR-010)  [DECISION — ver §5]
→ cancelar                                       [DECISION]
```

### 4.5 Pré-pedido

```
Reserva
→ visualizar cardápio
→ selecionar pratos
→ definir quantidades
→ enviar pré-pedido (SUBMITTED)
→ alterar / cancelar dentro das regras         [TBD — D1]
```

### 4.6 Avaliação

```
Reserva concluída (COMPLETED)
→ cliente avalia o restaurante (uma vez por reserva) [DECISION — ADR-007/012]
→ avalia pratos elegíveis (pré-pedido; cada prato uma vez) [DECISION — ADR-007/012]
→ sem edição da avaliação no MVP                 [DECISION — ADR-012]
→ admin pode moderar (PUBLISHED/HIDDEN)           [DECISION]
→ admin pode responder                            [DECISION]
```

### 4.7 Evento

```
Cliente
→ solicita evento
→ PENDING
→ Admin analisa
→ APPROVED / REJECTED            [DECISION]
→ Cliente pode cancelar         [DECISION — CANCELLED]
```

---

## 5. Regras importantes

> Cada regra está marcada `[DECISION]` (definida) ou `TODO — DECISÃO NECESSÁRIA` (aberta). Não se inventam regras não definidas.

### 5.1 Regras de reserva

| # | Regra | Estado |
| --- | --- | --- |
| R1 | A reserva possui **data** | `[DECISION]` |
| R2 | A reserva possui **horário** | `[DECISION]` |
| R3 | A reserva possui **duração** | `[DECISION]` |
| R4 | A duração é escolhida pelo cliente **dentro dos limites configurados** pelo restaurante | `[DECISION]` |
| R5 | A quantidade de pessoas determina a necessidade de mesas | `[DECISION]` (ADR-005) |
| R6 | As mesas podem ser alocadas dinamicamente | `[DECISION]` (ADR-005) |
| R7 | O admin define as regras de capacidade (CapacityRule) | `[DECISION]` |
| R8 | As mesas podem ser bloqueadas pelo admin | `[DECISION]` |
| R9 | Reservas não podem conflitar no mesmo recurso/horário — uma mesa não pode estar em duas reservas com intervalos sobrepostos | `[DECISION]` (ADR-011) |
| R10 | O cliente pode **editar** a reserva | `[DECISION]` |
| R11 | O cliente pode **alterar o horário** | `[DECISION]` |
| R12 | O cliente pode **cancelar** | `[DECISION]` |
| R13 | O admin pode cancelar | `[DECISION]` |
| R14 | Existe uma **janela de cancelamento** configurável | `[DECISION]` — default 60 min (1 hora) antes do início (ADR-010) |
| R15 | O cliente **não pode ter duas reservas simultâneas** | `[DECISION]` — semântica exata `[TBD]` (não bloqueante) |

**Valores padrão de reserva (D2 — ADR-010):** defaults do restaurante, configuráveis pelo ADMIN em `RestaurantSettings` (**não são constantes do domínio**): duração mínima **30 min**; duração máxima **3 h (180 min)**; incremento de duração **30 min**; antecedência mínima para reservar **1 hora**; antecedência máxima **90 dias**; cancelamento permitido até **1 hora antes do início**.

**Overlap (D4 — ADR-011):** uma mesma mesa física não pode estar associada a duas reservas cujos intervalos se sobreponham. Intervalos adjacentes são permitidos (ex.: 19:00→21:00 e 21:00→23:00 na mesma mesa); 19:00→21:00 e 20:00→22:00 na mesma mesa é **inválido**. A validação ocorre no backend e a operação de criação/alocação é **transacional**, evitando race conditions em reservas simultâneas.

### 5.2 Regras de avaliações

| # | Regra | Estado |
| --- | --- | --- |
| R16 | Avaliações só acontecem **após** a experiência/reserva concluída | `[DECISION]` (ADR-007) |
| R17 | Avaliação de prato depende de o prato estar associado à experiência/pré-pedido elegível | `[DECISION]` (ADR-007) |
| R18 | Quantidade de avaliações: **uma** avaliação de restaurante por reserva concluída; cada prato elegível avaliado uma única vez por avaliação; **sem edição** | `[DECISION]` (ADR-012) |

### 5.3 Regras do pré-pedido

| # | Regra | Estado |
| --- | --- | --- |
| R19 | O pré-pedido pode ser alterado/cancelado dentro das regras | `[DECISION]` — limites exatos `TODO — DECISÃO NECESSÁRIA` (D1) |

### 5.4 Fora do escopo (não-MVP)

| # | Regra | Estado |
| --- | --- | --- |
| R20 | **Pagamento** NÃO faz parte do MVP | `[DECISION]` (ADR-006) |
| R21 | **Delivery** NÃO faz parte do MVP | `[DECISION]` (ADR-006) |

---

> Fim de `PRODUCT_SPEC.md` — manter em sincronia com `DOMAIN_SPEC.md`, `API_SPEC.md`, `ROADMAP.md` e `DECISIONS.md`.