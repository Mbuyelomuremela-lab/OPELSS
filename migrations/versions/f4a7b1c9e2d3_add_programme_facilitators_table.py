"""add programme_facilitators table

Revision ID: f4a7b1c9e2d3
Revises: e1a2b3c4d5e6
Create Date: 2026-07-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f4a7b1c9e2d3'
down_revision: Union[str, Sequence[str], None] = 'e1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The app runs db.create_all() at startup, which may already have created
    # this table (e.g. on Azure where `flask db upgrade` imports the app first).
    # Guard so the migration is a no-op when the table already exists.
    bind = op.get_bind()
    if "programme_facilitators" in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        "programme_facilitators",
        sa.Column("programme_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["programme_id"], ["programmes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("programme_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    if "programme_facilitators" in sa.inspect(bind).get_table_names():
        op.drop_table("programme_facilitators")
