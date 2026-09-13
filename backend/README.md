# Blue backend

Backend do Blue v1 — **Fase 2: Backend Foundation** (ver [`docs/ROADMAP.md`](../docs/ROADMAP.md)).

Modular monolith (ADR-001) com Python + FastAPI + PostgreSQL + SQLAlchemy 2 + Alembic + Pydantic v2 + JWT + pytest.

## Requisitos

- Python ≥ 3.11
- PostgreSQL 16 (local). Opcional: `docker compose` (arquivo `docker-compose.yml` desta pasta).

> **Atenção (ambiente atual):** nesta máquina não há PostgreSQL nem Docker instalados (não há `psql`;
> a distro WSL Ubuntu também não tem PostgreSQL). A verificação ao vivo de banco/migrations fica
> pendente de um PostgreSQL acessível via `DATABASE_URL` — nada é simulado.

## Configuração

```powershell
cd backend
Copy-Item .env.example .env     # ajuste DATABASE_URL e segredos para o seu ambiente
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Variáveis (ver `.env.example`): `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`,
`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `ENVIRONMENT`, `LOG_LEVEL`.

## Banco local (opcional)

```powershell
docker compose up -d            # somente PostgreSQL (dev): blue/blue@localhost:5432/blue
```

## Migrations (Alembic — ADR-013)

```powershell
.\.venv\Scripts\alembic current          # exige banco acessível
.\.venv\Scripts\alembic heads
.\.venv\Scripts\alembic upgrade head      # aplica as migrations
.\.venv\Scripts\alembic revision --autogenerate -m "..."   # exige banco acessível
```

Sem banco acessível, ainda é possível validar a renderização offline:

```powershell
.\.venv\Scripts\alembic upgrade head --sql
```

## Rodar a API

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

- OpenAPI/docs: <http://127.0.0.1:8000/docs>
- `GET /health` — API no ar (independe de banco)
- `GET /health/db` — estado da conexão PostgreSQL (`200` ok / `503` indisponível)

## Bootstrap do primeiro ADMIN (CLI — ADR-016)

O primeiro `ADMIN` é criado por comando administrativo local — **não** pelo endpoint público
`POST /auth/register` (que cria somente `CUSTOMER`):

```powershell
.\.venv\Scripts\python -m app.cli create-admin
# ou com parte dos dados por argumento (a senha é sempre solicitada de forma segura):
.\.venv\Scripts\python -m app.cli create-admin --name "Operador" --email admin@blue.local
```

- solicita e-mail/nome (se omitidos) e a senha via `getpass` (sem eco, **nunca** por argumento);
- recusa e-mail já registrado (saída `1`);
- grava a senha somente como hash (Argon2) e **não** exibe credenciais;
- exige PostgreSQL acessível e migrations aplicadas (`alembic upgrade head`).

> Não existe endpoint público que crie `ADMIN` (`POST /auth/register-admin` não é implementado) nem
> é possível escolher `role` no cadastro público. Ver `docs/DECISIONS.md` — ADR-016.

## Testes

```powershell
pytest                          # unit + integration (integration é pulada sem PostgreSQL)
pytest -m "not integration"     # somente unitários (sem banco)
pytest -m integration           # exige PostgreSQL acessível
```

## Estrutura

```text
backend/
├── app/
│   ├── main.py                  # app FastAPI, routers, handlers de erro
│   ├── cli.py                   # CLI administrativa: bootstrap do ADMIN (ADR-016)
│   ├── core/                    # config, database, security, exceptions, dependencies, health
│   ├── modules/
│   │   ├── auth/                # foundation: register/login/me (JWT access token — ADR-014)
│   │   ├── users/               # User + UserRole (CUSTOMER/ADMIN — ADR-009) + service do ADMIN
│   │   └── restaurants/         # scaffold (models entram na Fase 3 — ver ADR-015)
│   └── shared/                  # reservado (sem código nesta fase)
├── migrations/                  # Alembic (env.py importa o metadata real)
├── tests/
│   ├── unit/                    # sem banco
│   └── integration/             # exigem PostgreSQL (auto-skip quando indisponível)
├── .env.example
├── alembic.ini
├── docker-compose.yml           # PostgreSQL local de desenvolvimento
└── pyproject.toml
```

## Escopo da fase (implementado)

- Estrutura modular `backend/` conforme `docs/ARCHITECTURE.md` §3.
- Configuração por ambiente (pydantic-settings), sem credenciais hardcoded.
- PostgreSQL/SQLAlchemy 2: engine, session factory, `Base`, dependency `get_db`.
- Alembic: `env.py` importa `Base.metadata` dos models; primeira migration **users**.
- JWT access token **sem refresh** (ADR-014); hashing Argon2 (`pwdlib`); roles `CUSTOMER`/`ADMIN` (ADR-009).
- Camadas router → schema → service → repository demonstradas em auth/users.
- Endpoints: `/health`, `/health/db` e `/auth/register|login|me` (foundation).
- Bootstrap do primeiro `ADMIN` via CLI (`python -m app.cli create-admin` — ADR-016); o
  cadastro público cria somente `CUSTOMER`.
- pytest: testes unitários sem banco + testes de integração marcados.

## Fase 3 — Restaurante & Reservas (implementado)

Models e endpoints de restaurante, mesas, regras de capacidade e reservas (ADR-017):

- `Restaurant`, `RestaurantSettings` (1:1, defaults ADR-010), `Table` (com `is_locked`),
  `CapacityRule` (faixa de pessoas → nº de mesas).
- `Reservation` + `ReservationTable` (N:N): criação/alteração/cancelamento **transacionais**,
  disponibilidade, alocação por `CapacityRule` e overlap por mesa (`SELECT ... FOR UPDATE`).
- Migrations `66e313a02830` (restaurante) e `880549f32c7d` (reservas), sobre `3bc98a491108`.

Contratos em `docs/API_SPEC.md` §1.1/§6/§7/§8/§14. A verificação end-to-end permanece pendente de um
PostgreSQL real (os testes de integração são pulados sem banco).

## Fora desta fase (fases posteriores)

Módulos de negócio ainda não implementados: `menu`, `preorders`, `reviews`, `events`,
`notifications`. Decisões abertas (`D1`/`D3`/`D9`/`D10`/`D11`, R15) seguem `[TBD]`. Ver `docs/ROADMAP.md`.
A criação do primeiro `ADMIN` **já faz parte da fundação**, via CLI (ADR-016) — ver seção acima.
