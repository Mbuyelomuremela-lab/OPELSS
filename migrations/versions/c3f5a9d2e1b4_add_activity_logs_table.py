"""add activity_logs table

Revision ID: c3f5a9d2e1b4
Revises: b7e1c2a4d9f0
Create Date: 2026-06-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f5a9d2e1b4'
down_revision: Union[str, Sequence[str], None] = 'b7e1c2a4d9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The app runs db.create_all() at startup, which may already have created
    # this table (e.g. on Azure where `flask db upgrade` imports the app first).
    # Guard so the migration is a no-op when the table already exists.
    bind = op.get_bind()
    if "activity_logs" in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("actor_name", sa.String(length=120), nullable=False),
        sa.Column("actor_role", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("entity_label", sa.String(length=255), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    if "activity_logs" in sa.inspect(bind).get_table_names():
        op.drop_table("activity_logs")
