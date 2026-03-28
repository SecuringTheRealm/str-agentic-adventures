"""add unique constraint on save_slots(campaign_id, slot_number)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-28 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add UNIQUE(campaign_id, slot_number) to save_slots.

    Uses batch mode for SQLite compatibility (SQLite does not support
    ALTER TABLE ADD CONSTRAINT).
    """
    with op.batch_alter_table("save_slots") as batch_op:
        batch_op.create_unique_constraint(
            "uq_save_slot_campaign_slot",
            ["campaign_id", "slot_number"],
        )


def downgrade() -> None:
    """Remove UNIQUE(campaign_id, slot_number) from save_slots."""
    with op.batch_alter_table("save_slots") as batch_op:
        batch_op.drop_constraint(
            "uq_save_slot_campaign_slot",
            type_="unique",
        )
