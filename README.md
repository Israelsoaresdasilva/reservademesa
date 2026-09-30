# Ocean Blue - Sistema de Reservas e Cardápio

Este projeto é um sistema para restaurante com visualização de mesas, cardápio digital,
avaliações e **reservas full-stack**. O frontend é React + TypeScript + Vite; o backend é
Python + FastAPI + PostgreSQL (as reservas são persistidas em banco, sem login).

## Desenvolvidos por

Keila da cunha rezende - 06015370
Israel Soares da Silva - 06010016
Matheus Prudente Silva - 06003440
Savio Emmanuel Silva da Conceição - 06009864
Patrick Quintino - 06016924

## O que foi implementado (resumo)

- **Fluxo de reserva full-stack**: o formulário do site (nome, CPF, telefone, número de
  pessoas, data, horário e mesa) agora é salvo no PostgreSQL via API, em vez de `localStorage`.
- **Regra de negócio no backend**: um mesmo CPF não pode ter duas reservas na mesma data
  (`UNIQUE(cpf, data)` no banco → `409 Conflict`).
- **API pública de reservas** (`/api/reservas`): criar, listar (com filtro por data), detalhar
  e excluir.
- **Painel administrativo** em `/admin/reservas` para ver e excluir as reservas do dia (protegido por login).

## Como executar

### 1. Frontend (site)

```bash
npm install
npm run dev
```

- Site: [http://localhost:5173/](http://localhost:5173/)
- Painel administrativo: [http://localhost:5173/admin/reservas](http://localhost:5173/admin/reservas)
  - Login: usuário `oceanblueadm` · senha `blue2026`

O frontend fala com o backend pela variável `VITE_API_URL` (default `http://localhost:8000`).
Se precisar trocar, copie `.env.example` para `.env` e ajuste o valor.

### 2. Backend (API FastAPI)

```bash
cd backend
python -m venv .venv
# Windows (Git Bash / PowerShell):
./.venv/Scripts/python -m pip install -e ".[dev]"
# Linux/macOS:
source .venv/bin/activate && pip install -e ".[dev]"
```

Crie o `.env` a partir do `.env.example` e defina a `DATABASE_URL` (PostgreSQL ou Neon):

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/nome_do_banco
```

Aplique as migrations e suba a API:

```bash
./.venv/Scripts/alembic upgrade head
./.venv/Scripts/python -m uvicorn app.main:app --reload
```

- Documentação da API (OpenAPI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: `GET /health` e `GET /health/db`

## API de reservas

Endpoints públicos (sem autenticação):

| Método | Endpoint | Descrição |
| --- | --- | --- |
| `POST` | `/api/reservas` | Cria a reserva. `409` se o CPF já tiver reserva na mesma data. |
| `GET` | `/api/reservas?data=YYYY-MM-DD` | Lista reservas (filtro por data opcional), ordenadas por horário. |
| `GET` | `/api/reservas/{id}` | Detalhe da reserva. |
| `DELETE` | `/api/reservas/{id}` | Exclui a reserva (uso administrativo). |

Exemplo de corpo do `POST`:

```json
{
  "nome": "João Silva",
  "cpf": "123.456.789-00",
  "telefone": "21999999999",
  "numeroPessoas": 4,
  "data": "2026-10-30",
  "horario": "19:30",
  "mesa": "12"
}
```

Respostas no formato `{ "success": true|false, ... }`. Detalhes adicionais do backend em
[`backend/README.md`](./backend/README.md).

## Estrutura do Projeto

```
reservademesa/
├── src/
│   ├── main.tsx                 # rotas ( / e /admin/reservas )
│   ├── App.tsx                  # home + modais (cardápio, reserva, avaliações)
│   ├── services/                # integração com o backend
│   │   ├── api.ts               # cliente HTTP (VITE_API_URL)
│   │   └── reservasService.ts   # criar/listar/excluir reservas
│   ├── Pages/
│   │   ├── homepage.tsx         # página inicial
│   │   ├── reservas/            # fluxo de reserva + mapa de mesas
│   │   ├── admin/               # painel administrativo (/admin/reservas)
│   │   └── avaliacoes.tsx       # avaliações
│   └── features/notifications/  # sistema de notificações
├── backend/                     # API FastAPI + migrations (Alembic)
│   ├── app/modules/reservas/    # módulo da reserva pública (/api/reservas)
│   └── migrations/
├── public/                      # assets estáticos e Cardápio.html
├── .env.example                 # VITE_API_URL
└── package.json
```

## Observações

- O cardápio é mantido em `public/Cardápio.html` (layout original preservado).
- As rotas SPA são gerenciadas pelo React Router (`/` e `/admin/reservas`).
- O projeto utiliza Vite.
- `node_modules/`, `dist/` e `backend/.venv/` são ignorados pelo Git.
- O backend **não** exige login para o fluxo de reserva do cliente. O painel administrativo
  (`/admin/reservas`) usa um login fixo de demonstração: usuário `oceanblueadm`, senha `blue2026`.
