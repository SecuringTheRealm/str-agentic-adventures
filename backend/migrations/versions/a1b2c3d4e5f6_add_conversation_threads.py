"""add conversation threads

Revision ID: a1b2c3d4e5f6
Revises: 50b401563356, 640db23039c0
Create Date: 2026-03-26 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = ("50b401563356", "640db23039c0")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create conversation_threads table."""
    op.create_table(
        "conversation_threads",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=True),
        sa.Column("agent_name", sa.String(), nullable=False),
        sa.Column("messages", sa.JSON(), nullable=False),
        sa.Column("sdk_thread_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "agent_name", name="uq_thread_session_agent"),
    )
    # Fix pre-existing migration gap: conversation_history column was added to
    # NPCProfileDB model in PR #554 but not included in a migration
    op.add_column(
        "npc_profiles",
        sa.Column("conversation_history", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.create_index(
        op.f("ix_conversation_threads_id"),
        "conversation_threads",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_threads_session_id"),
        "conversation_threads",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_threads_campaign_id"),
        "conversation_threads",
        ["campaign_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop conversation_threads table and revert conversation_history column."""
    op.drop_column("npc_profiles", "conversation_history")
    op.drop_index(
        op.f("ix_conversation_threads_campaign_id"),
        table_name="conversation_threads",
    )
    op.drop_index(
        op.f("ix_conversation_threads_session_id"),
        table_name="conversation_threads",
    )
    op.drop_index(
        op.f("ix_conversation_threads_id"),
        table_name="conversation_threads",
    )
    op.drop_table("conversation_threads")
