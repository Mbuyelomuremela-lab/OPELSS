"""add asset fault description

Revision ID: a1c7e4f0b2d9
Revises: f4a7b1c9e2d3
Create Date: 2026-07-24 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a1c7e4f0b2d9'
down_revision: Union[str, Sequence[str], None] = 'f4a7b1c9e2d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # PostgreSQL supports IF NOT EXISTS — safe to run even if the column exists
        bind.execute(sa.text('ALTER TABLE assets ADD COLUMN IF NOT EXISTS fault_description TEXT'))
    else:
        # SQLite needs batch_alter_table; check manually to avoid duplicates
        existing = {row[1] for row in bind.execute(sa.text('PRAGMA table_info(assets)')).fetchall()}
        if 'fault_description' not in existing:
            with op.batch_alter_table('assets') as batch_op:
                batch_op.add_column(sa.Column('fault_description', sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        bind.execute(sa.text('ALTER TABLE assets DROP COLUMN IF EXISTS fault_description'))
    else:
        with op.batch_alter_table('assets') as batch_op:
            batch_op.drop_column('fault_description')
