"""add game sessions and participants

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create game_sessions and session_participants tables."""
    op.create_table(
        "game_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("turn_order", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("current_turn_index", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_game_sessions_id"), "game_sessions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_game_sessions_campaign_id"),
        "game_sessions",
        ["campaign_id"],
        unique=False,
    )

    op.create_table(
        "session_participants",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("character_id", sa.String(), nullable=False),
        sa.Column("player_name", sa.String(), nullable=False),
        sa.Column("is_dm", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_connected", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"]),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_session_participants_id"),
        "session_participants",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_session_participants_session_id"),
        "session_participants",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop session_participants and game_sessions tables."""
    op.drop_index(
        op.f("ix_session_participants_session_id"),
        table_name="session_participants",
    )
    op.drop_index(
        op.f("ix_session_participants_id"),
        table_name="session_participants",
    )
    op.drop_table("session_participants")
    op.drop_index(
        op.f("ix_game_sessions_campaign_id"), table_name="game_sessions"
    )
    op.drop_index(op.f("ix_game_sessions_id"), table_name="game_sessions")
    op.drop_table("game_sessions")
