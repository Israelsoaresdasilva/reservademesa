""" create restaurant domain tables

Revision ID: 66e313a02830
Revises: 3bc98a491108
Create Date: 2026-09-11 22:36:51.538483
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66e313a02830'
down_revision: Union[str, None] = '3bc98a491108'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TIMESTAMP = sa.DateTime(timezone=True)
_TIMESTAMP_DEFAULT = sa.text("(CURRENT_TIMESTAMP)")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at", _TIMESTAMP, server_default=_TIMESTAMP_DEFAULT, nullable=False
        ),
        sa.Column(
            "updated_at", _TIMESTAMP, server_default=_TIMESTAMP_DEFAULT, nullable=False
        ),
    ]


def upgrade() -> None:
    # `Restaurant` (docs/DOMAIN_SPEC.md §2.2)
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_restaurants_slug"), "restaurants", ["slug"], unique=True)

    # `RestaurantSettings` 1:1 (§2.3). Os defaults do ADR-010 são aplicados pelo ORM,
    # por isso as colunas não têm `server_default`.
    op.create_table(
        "restaurant_settings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("cancellation_window_minutes", sa.Integer(), nullable=False),
        sa.Column("min_booking_lead_minutes", sa.Integer(), nullable=False),
        sa.Column("max_booking_lead_days", sa.Integer(), nullable=False),
        sa.Column("max_people_per_reservation", sa.Integer(), nullable=False),
        sa.Column("min_people_per_reservation", sa.Integer(), nullable=False),
        sa.Column("reservation_min_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("reservation_max_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("reservation_duration_step_minutes", sa.Integer(), nullable=False),
        sa.Column("preorder_enabled", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "cancellation_window_minutes >= 0",
            name="ck_restaurant_settings_cancellation_window",
        ),
        sa.CheckConstraint(
            "min_booking_lead_minutes >= 0", name="ck_restaurant_settings_min_lead"
        ),
        sa.CheckConstraint(
            "max_booking_lead_days >= 1", name="ck_restaurant_settings_max_lead_days"
        ),
        sa.CheckConstraint(
            "min_people_per_reservation >= 1", name="ck_restaurant_settings_min_people"
        ),
        sa.CheckConstraint(
            "max_people_per_reservation >= min_people_per_reservation",
            name="ck_restaurant_settings_people_range",
        ),
        sa.CheckConstraint(
            "reservation_min_duration_minutes >= 1",
            name="ck_restaurant_settings_min_duration",
        ),
        sa.CheckConstraint(
            "reservation_max_duration_minutes >= reservation_min_duration_minutes",
            name="ck_restaurant_settings_duration_range",
        ),
        sa.CheckConstraint(
            "reservation_duration_step_minutes BETWEEN "
            "reservation_min_duration_minutes AND reservation_max_duration_minutes",
            name="ck_restaurant_settings_duration_step",
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id", name="uq_restaurant_settings_restaurant"),
    )


    # `Table` (§2.4)
    op.create_table(
        "tables",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=40), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("is_locked", sa.Boolean(), nullable=False),
        sa.Column("position_x", sa.Float(), nullable=True),
        sa.Column("position_y", sa.Float(), nullable=True),
        sa.Column("position_z", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("capacity >= 1", name="ck_tables_capacity_positive"),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id", "label", name="uq_tables_restaurant_label"),
    )
    op.create_index(
        op.f("ix_tables_restaurant_id"), "tables", ["restaurant_id"], unique=False
    )

    # `CapacityRule` (§2.5)
    op.create_table(
        "capacity_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("min_people", sa.Integer(), nullable=False),
        sa.Column("max_people", sa.Integer(), nullable=False),
        sa.Column("tables_required", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("min_people >= 1", name="ck_capacity_rules_min_people"),
        sa.CheckConstraint("max_people >= min_people", name="ck_capacity_rules_range"),
        sa.CheckConstraint(
            "tables_required >= 1", name="ck_capacity_rules_tables_required"
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_capacity_rules_restaurant_id"),
        "capacity_rules",
        ["restaurant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_capacity_rules_restaurant_id"), table_name="capacity_rules")
    op.drop_table("capacity_rules")
    op.drop_index(op.f("ix_tables_restaurant_id"), table_name="tables")
    op.drop_table("tables")
    op.drop_table("restaurant_settings")
    op.drop_index(op.f("ix_restaurants_slug"), table_name="restaurants")
    op.drop_table("restaurants")
