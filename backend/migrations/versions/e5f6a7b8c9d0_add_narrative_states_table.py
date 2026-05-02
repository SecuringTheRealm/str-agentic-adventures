"""add narrative_states table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-02 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: str | Sequence[str] | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the narrative_states table."""
    op.create_table(
        "narrative_states",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column(
            "campaign_id",
            sa.String(),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Drop the narrative_states table."""
    op.drop_table("narrative_states")
