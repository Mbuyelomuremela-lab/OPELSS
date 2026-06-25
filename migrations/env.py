from __future__ import with_statement

import logging
import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from flask import current_app

config = context.config
config_file_name = config.config_file_name
if config_file_name is None:
    config_file_name = str(Path(__file__).resolve().parents[1] / "alembic.ini")
elif not os.path.isabs(config_file_name):
    local_path = Path(config_file_name)
    root_candidate = Path(__file__).resolve().parents[1] / local_path.name
    if not local_path.exists() and root_candidate.exists():
        config_file_name = str(root_candidate)
fileConfig(config_file_name)
logger = logging.getLogger('alembic.env')

config.set_main_option('sqlalchemy.url', current_app.config.get('SQLALCHEMY_DATABASE_URI'))

target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Use the Flask app's configured engine so migrations always target the
    # real database (DATABASE_URL / SQLALCHEMY_DATABASE_URI). Building the engine
    # from the alembic.ini section instead would silently fall back to its
    # placeholder sqlalchemy.url (sqlite:///app.db).
    connectable = current_app.extensions['migrate'].db.engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# Alembic executes this module with __name__ set to the module name (not
# "__main__"), so the migrations must be invoked at import time — guarding this
# behind `if __name__ == "__main__"` would silently skip every migration.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
