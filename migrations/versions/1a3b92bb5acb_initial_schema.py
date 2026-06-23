"""Initial schema

Revision ID: 1a3b92bb5acb
Revises: 
Create Date: 2026-04-17 22:19:37.192988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app import create_app
from app.extensions import db as _db


# revision identifiers, used by Alembic.
revision: str = '1a3b92bb5acb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create all tables from the application's models as the initial schema.
    app = create_app()
    with app.app_context():
        _db.create_all()


def downgrade() -> None:
    """Downgrade schema."""
    # Drop all tables created by the models (used only for local/dev rollback).
    app = create_app()
    with app.app_context():
        _db.drop_all()
