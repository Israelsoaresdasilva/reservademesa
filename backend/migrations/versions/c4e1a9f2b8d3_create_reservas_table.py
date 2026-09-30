"""create reservas table

Revision ID: c4e1a9f2b8d3
Revises: 880549f32c7d
Create Date: 2026-09-30 22:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4e1a9f2b8d3"
down_revision: Union[str, None] = "880549f32c7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TIMESTAMP = sa.DateTime(timezone=True)
_TIMESTAMP_DEFAULT = sa.text("(CURRENT_TIMESTAMP)")


def upgrade() -> None:
    # `Reserva` (fluxo público — roadmap da raiz). Regra principal: UNIQUE(cpf, data).
    op.create_table(
        "reservas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("cpf", sa.String(length=11), nullable=False),
        sa.Column("telefone", sa.String(length=32), nullable=False),
        sa.Column("numero_pessoas", sa.Integer(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("horario", sa.Time(), nullable=False),
        sa.Column("mesa", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            _TIMESTAMP,
            server_default=_TIMESTAMP_DEFAULT,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            _TIMESTAMP,
            server_default=_TIMESTAMP_DEFAULT,
            nullable=False,
        ),
        sa.CheckConstraint(
            "numero_pessoas >= 1", name="ck_reservas_numero_pessoas_positive"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf", "data", name="uq_reservas_cpf_data"),
    )
    op.create_index(op.f("ix_reservas_cpf"), "reservas", ["cpf"], unique=False)
    op.create_index(op.f("ix_reservas_data"), "reservas", ["data"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reservas_data"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_cpf"), table_name="reservas")
    op.drop_table("reservas")
