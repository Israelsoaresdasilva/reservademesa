# Blue backend

Backend do Blue v1 — **Fase 2: Backend Foundation** (ver [`docs/ROADMAP.md`](../docs/ROADMAP.md)).

Modular monolith (ADR-001) com Python + FastAPI + PostgreSQL + SQLAlchemy 2 + Alembic + Pydantic v2 + JWT + pytest.

## Requisitos

- Python ≥ 3.11
- PostgreSQL 16 (local). Opcional: `docker compose` (arquivo `docker-compose.yml` desta pasta).

> **Atenção (ambiente atual):** nesta máquina não há PostgreSQL nem Docker instalados. A verificação
> ao vivo de banco/migrations fica pendente de um PostgreSQL acessível via `DATABASE_URL` — nada é simulado.

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
│   ├── core/                    # config, database, security, exceptions, dependencies, health
│   ├── modules/
│   │   ├── auth/                # foundation: register/login/me (JWT access token — ADR-014)
│   │   ├── users/               # User + UserRole (CUSTOMER/ADMIN — ADR-009)
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
- pytest: testes unitários sem banco + testes de integração marcados.

## Fora desta fase

Módulos de negócio (reservations, tables, menu, preorders, reviews, events, notifications),
models de restaurante (`Restaurant`/`RestaurantSettings`/`CapacityRule`) e criação/seed de
`ADMIN` (D6 `[TBD]`). Ver `docs/ROADMAP.md`.
