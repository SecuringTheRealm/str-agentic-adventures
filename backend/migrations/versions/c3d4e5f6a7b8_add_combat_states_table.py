"""add combat_states table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-28 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create combat_states table for persistent combat encounters."""
    op.create_table(
        "combat_states",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("round", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("current_turn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("initiative_order", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("participants", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("environment", sa.String(), nullable=False, server_default="standard"),
        sa.Column("combat_log", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_combat_states_id"), "combat_states", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_combat_states_session_id"),
        "combat_states",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop combat_states table."""
    op.drop_index(
        op.f("ix_combat_states_session_id"), table_name="combat_states"
    )
    op.drop_index(op.f("ix_combat_states_id"), table_name="combat_states")
    op.drop_table("combat_states")
