"""merge ef3c1051f7e0 and c8f9b3aa1d5c

Revision ID: 9d89f7175be1
Revises: ef3c1051f7e0, c8f9b3aa1d5c
Create Date: 2026-01-21 14:55:22.110625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d89f7175be1'
down_revision: Union[str, Sequence[str], None] = ('ef3c1051f7e0', 'c8f9b3aa1d5c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
