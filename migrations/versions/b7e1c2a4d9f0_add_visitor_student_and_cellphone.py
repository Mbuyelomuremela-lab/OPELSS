"""add visitor student_number and cellphone_number

Revision ID: b7e1c2a4d9f0
Revises: d52a68fff2c6
Create Date: 2026-06-25 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e1c2a4d9f0'
down_revision: Union[str, Sequence[str], None] = 'd52a68fff2c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("visitors") as batch_op:
        batch_op.add_column(sa.Column("student_number", sa.String(length=8), nullable=True))
        batch_op.add_column(sa.Column("cellphone_number", sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("visitors") as batch_op:
        batch_op.drop_column("cellphone_number")
        batch_op.drop_column("student_number")
