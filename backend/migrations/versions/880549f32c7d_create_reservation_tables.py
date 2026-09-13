""" create reservation tables

Revision ID: 880549f32c7d
Revises: 66e313a02830
Create Date: 2026-09-11 22:36:58.683641
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '880549f32c7d'
down_revision: Union[str, None] = '66e313a02830'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TIMESTAMP = sa.DateTime(timezone=True)
_TIMESTAMP_DEFAULT = sa.text("(CURRENT_TIMESTAMP)")


def upgrade() -> None:
    # `Reservation` (docs/DOMAIN_SPEC.md §2.6). `date` + `start_time` conforme o domínio;
    # o instante de início (`start_at`, UTC) é derivado na aplicação.
    op.create_table(
        "reservations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("people_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "CONFIRMED",
                "CANCELLED",
                "COMPLETED",
                "NO_SHOW",
                name="reservationstatus",
                native_enum=False,
                length=20,
                create_constraint=False,
            ),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "cancelled_by",
            sa.Enum(
                "CUSTOMER",
                "ADMIN",
                name="userrole",
                native_enum=False,
                length=20,
                create_constraint=False,
            ),
            nullable=True,
        ),
        sa.Column("cancelled_at", _TIMESTAMP, nullable=True),
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
            "duration_minutes > 0", name="ck_reservations_duration_positive"
        ),
        sa.CheckConstraint("people_count >= 1", name="ck_reservations_people_positive"),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reservations_date"), "reservations", ["date"], unique=False
    )
    op.create_index(
        op.f("ix_reservations_restaurant_id"),
        "reservations",
        ["restaurant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reservations_status"), "reservations", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_reservations_user_id"), "reservations", ["user_id"], unique=False
    )


    # `ReservationTable` (§2.7 — associação N:N, ADR-004)
    op.create_table(
        "reservation_tables",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("reservation_id", sa.Uuid(), nullable=False),
        sa.Column("table_id", sa.Uuid(), nullable=False),
        sa.Column(
            "allocated_at",
            _TIMESTAMP,
            server_default=_TIMESTAMP_DEFAULT,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"], ["reservations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reservation_id",
            "table_id",
            name="uq_reservation_tables_reservation_table",
        ),
    )
    op.create_index(
        op.f("ix_reservation_tables_reservation_id"),
        "reservation_tables",
        ["reservation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reservation_tables_table_id"),
        "reservation_tables",
        ["table_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_reservation_tables_table_id"), table_name="reservation_tables"
    )
    op.drop_index(
        op.f("ix_reservation_tables_reservation_id"), table_name="reservation_tables"
    )
    op.drop_table("reservation_tables")
    op.drop_index(op.f("ix_reservations_user_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_status"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_restaurant_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_date"), table_name="reservations")
    op.drop_table("reservations")
