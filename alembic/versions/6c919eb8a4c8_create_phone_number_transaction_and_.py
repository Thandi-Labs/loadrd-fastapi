"""Create phone number transaction and user account tables

Revision ID: 6c919eb8a4c8
Revises: 
Create Date: 2026-06-17 20:09:16.532194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c919eb8a4c8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column(
        "phone_number", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
