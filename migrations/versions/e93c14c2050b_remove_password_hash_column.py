"""remove_password_hash_column

Revision ID: e93c14c2050b
Revises: be98bc6e414f
Create Date: 2025-12-29 05:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e93c14c2050b'
down_revision: Union[str, None] = 'be98bc6e414f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove password_hash column from users table.
    
    Auth0 handles all password management, so this column is no longer needed.
    """
    op.drop_column('users', 'password_hash')


def downgrade() -> None:
    """Revert migration - add password_hash column back."""
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))

