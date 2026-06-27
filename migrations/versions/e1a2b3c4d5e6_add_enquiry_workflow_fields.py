"""add enquiry workflow fields

Revision ID: e1a2b3c4d5e6
Revises: c3f5a9d2e1b4
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'c3f5a9d2e1b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COLUMNS = [
    ('escalation_reason', 'TEXT'),
    ('not_resolved_reason', 'TEXT'),
    ('assigned_by', 'INTEGER'),
    ('closed_by', 'INTEGER'),
    ('escalated_at', 'TIMESTAMP'),
    ('assigned_at', 'TIMESTAMP'),
    ('in_progress_at', 'TIMESTAMP'),
    ('resolved_at', 'TIMESTAMP'),
    ('closed_at', 'TIMESTAMP'),
]


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # PostgreSQL supports IF NOT EXISTS — safe to run even if columns exist
        for col, col_type in _COLUMNS:
            bind.execute(
                sa.text(f'ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS {col} {col_type}')
            )
    else:
        # SQLite needs batch_alter_table; check manually to avoid duplicates
        existing = {row[1] for row in bind.execute(sa.text('PRAGMA table_info(enquiries)')).fetchall()}
        with op.batch_alter_table('enquiries') as batch_op:
            for col, col_type in _COLUMNS:
                if col not in existing:
                    batch_op.add_column(sa.Column(col, sa.Text() if col_type == 'TEXT' else sa.Integer() if col_type == 'INTEGER' else sa.DateTime(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        for col, _ in _COLUMNS:
            bind.execute(sa.text(f'ALTER TABLE enquiries DROP COLUMN IF EXISTS {col}'))
    else:
        with op.batch_alter_table('enquiries') as batch_op:
            for col, _ in reversed(_COLUMNS):
                batch_op.drop_column(col)
