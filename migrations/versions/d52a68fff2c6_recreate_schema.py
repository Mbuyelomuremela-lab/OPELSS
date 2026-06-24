"""recreate schema

Revision ID: d52a68fff2c6
Revises: 0d08371166eb
Create Date: 2026-06-24 10:06:29.279648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd52a68fff2c6'
down_revision: Union[str, Sequence[str], None] = '0d08371166eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
