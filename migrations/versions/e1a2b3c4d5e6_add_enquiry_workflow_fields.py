"""add enquiry workflow fields

Revision ID: e1a2b3c4d5e6
Revises: d52a68fff2c6
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd52a68fff2c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('enquiries') as batch_op:
        batch_op.add_column(sa.Column('escalation_reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('not_resolved_reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('assigned_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
        batch_op.add_column(sa.Column('closed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
        batch_op.add_column(sa.Column('escalated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('assigned_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('in_progress_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('resolved_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('closed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('enquiries') as batch_op:
        batch_op.drop_column('escalation_reason')
        batch_op.drop_column('not_resolved_reason')
        batch_op.drop_column('assigned_by')
        batch_op.drop_column('closed_by')
        batch_op.drop_column('escalated_at')
        batch_op.drop_column('assigned_at')
        batch_op.drop_column('in_progress_at')
        batch_op.drop_column('resolved_at')
        batch_op.drop_column('closed_at')
