"""add unique mesa+data to reservas

Revision ID: d5e6f7a8b9c0
Revises: c4e1a9f2b8d3
Create Date: 2026-09-30 23:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4e1a9f2b8d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Uma mesma mesa não pode ter duas reservas no mesmo dia.
    op.create_unique_constraint("uq_reservas_mesa_data", "reservas", ["mesa", "data"])


def downgrade() -> None:
    op.drop_constraint("uq_reservas_mesa_data", "reservas", type_="unique")
