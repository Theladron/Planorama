"""remove_is_admin_column

Revision ID: 30d3fed2d112
Revises: e93c14c2050b
Create Date: 2025-12-29 06:26:26.750740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30d3fed2d112'
down_revision: Union[str, None] = 'e93c14c2050b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove is_admin column from users table.
    
    Admin status is now determined by Auth0 roles in the JWT token,
    not stored in the database.
    """
    op.drop_column('users', 'is_admin')


def downgrade() -> None:
    """Restore is_admin column to users table."""
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
