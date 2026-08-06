"""remap users to HQ job-function roles

Splits the old coarse roles (Admin / HQ Trainee) into job-function roles.
No schema change — users.role is already VARCHAR(50). This is a data-only
migration:

  * the two named developers  -> 'Developers'
  * every other HQ account    -> 'Manager' (full access minus the Admin console)
  * 'Lab Trainee' accounts     -> left completely untouched

Managers/Developers then reassign each person to their precise role from the
Admin console.

Revision ID: b2d9c4e7a1f3
Revises: a1c7e4f0b2d9
Create Date: 2026-08-06 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2d9c4e7a1f3'
down_revision: Union[str, Sequence[str], None] = 'a1c7e4f0b2d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEVELOPER_EMAILS = (
    'mbuyelo-muremm@unisa.ac.za',
    'zuhlume-sigwaz@unisa.ac.za',
)


def upgrade() -> None:
    bind = op.get_bind()

    # 1) The two named developers become 'Developers' (only role with the console).
    bind.execute(
        sa.text(
            "UPDATE users SET role = 'Developers' "
            "WHERE LOWER(email) IN (:e1, :e2)"
        ),
        {"e1": DEVELOPER_EMAILS[0], "e2": DEVELOPER_EMAILS[1]},
    )

    # 2) Every other existing HQ account defaults to 'Manager' so nobody is
    #    locked out mid-pilot. Lab Trainee accounts are intentionally excluded.
    bind.execute(
        sa.text(
            "UPDATE users SET role = 'Manager' "
            "WHERE role IN ('Admin', 'HQ Trainee') "
            "AND LOWER(email) NOT IN (:e1, :e2)"
        ),
        {"e1": DEVELOPER_EMAILS[0], "e2": DEVELOPER_EMAILS[1]},
    )


def downgrade() -> None:
    bind = op.get_bind()

    # Collapse the job-function roles back to the old two HQ roles.
    bind.execute(
        sa.text(
            "UPDATE users SET role = 'Admin' "
            "WHERE role IN ('Developers', 'Manager', 'Senior resource manager')"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE users SET role = 'HQ Trainee' "
            "WHERE role IN ('Trainee student support', 'Senior student support', "
            "'Trainee multimedia', 'Senior multimedia', 'Trainee resource manager')"
        )
    )
