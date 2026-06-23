"""add announcements table

Revision ID: 0d08371166eb
Revises: 1a3b92bb5acb
Create Date: 2026-04-17 22:26:21.051867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d08371166eb'
down_revision: Union[str, Sequence[str], None] = '1a3b92bb5acb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No-op: announcements table created by initial schema migration.
    return


def downgrade() -> None:
    """Downgrade schema."""
    return
