"""add npc tables

Revision ID: 640db23039c0
Revises: 9a6d5baf6502
Create Date: 2026-03-25 19:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "640db23039c0"
down_revision: str | Sequence[str] | None = "9a6d5baf6502"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create npc_profiles and npc_relationships tables."""
    op.create_table(
        "npc_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("personality_traits", sa.JSON(), nullable=False),
        sa.Column("disposition", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("is_alive", sa.Boolean(), nullable=False),
        sa.Column("conversation_notes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_npc_profiles_id"), "npc_profiles", ["id"], unique=False)
    op.create_index(
        op.f("ix_npc_profiles_campaign_id"),
        "npc_profiles",
        ["campaign_id"],
        unique=False,
    )

    op.create_table(
        "npc_relationships",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("npc_id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("disposition_score", sa.Integer(), nullable=False),
        sa.Column("interactions_count", sa.Integer(), nullable=False),
        sa.Column("key_events", sa.JSON(), nullable=False),
        sa.Column("last_interaction", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["npc_id"], ["npc_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_npc_relationships_id"), "npc_relationships", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_npc_relationships_npc_id"),
        "npc_relationships",
        ["npc_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_npc_relationships_campaign_id"),
        "npc_relationships",
        ["campaign_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop npc_profiles and npc_relationships tables."""
    op.drop_index(op.f("ix_npc_relationships_campaign_id"), table_name="npc_relationships")
    op.drop_index(op.f("ix_npc_relationships_npc_id"), table_name="npc_relationships")
    op.drop_index(op.f("ix_npc_relationships_id"), table_name="npc_relationships")
    op.drop_table("npc_relationships")
    op.drop_index(op.f("ix_npc_profiles_campaign_id"), table_name="npc_profiles")
    op.drop_index(op.f("ix_npc_profiles_id"), table_name="npc_profiles")
    op.drop_table("npc_profiles")
