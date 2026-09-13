"""Módulo `users` — identidade e acesso.

Entidades (docs/DOMAIN_SPEC.md §2.1 e §4.1):
- `User`: id UUID, name, email único, phone?, password_hash, role, is_active, created_at/updated_at.
- `UserRole`: somente `CUSTOMER` e `ADMIN` (ADR-009).

Nesta fase o módulo é usado pela fundação de autenticação (`auth`).

O primeiro `ADMIN` é criado por **bootstrap administrativo** (CLI
`python -m app.cli create-admin` → `users.service.create_admin_user`) e **nunca**
pelo cadastro público — `POST /auth/register` cria somente `CUSTOMER` (ADR-016).
"""
