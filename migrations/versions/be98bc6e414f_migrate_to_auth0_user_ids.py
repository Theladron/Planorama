"""migrate_to_auth0_user_ids

Revision ID: be98bc6e414f
Revises: 349b02c05c8d
Create Date: 2025-12-29 03:10:55.047904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be98bc6e414f'
down_revision: Union[str, None] = '349b02c05c8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate to Auth0 user IDs.
    
    Changes:
    1. Change users.id from Integer to String(255) (to store Auth0 user IDs)
    2. Change trips.user_id from Integer to String(255) (to match users.id)
    3. Make users.password_hash nullable (Auth0 handles passwords)
    """
    # Step 1: Make password_hash nullable
    op.alter_column('users', 'password_hash',
                   existing_type=sa.String(length=128),
                   nullable=True)
    
    # Step 3: Change trips.user_id to String
    # Drop foreign key constraint first
    op.drop_constraint('trips_user_id_fkey', 'trips', type_='foreignkey')
    
    # Add new column
    op.add_column('trips', sa.Column('user_id_new', sa.String(length=255), nullable=True))
    
    # Copy data (convert int to string) - this will be empty for fresh database
    op.execute("UPDATE trips SET user_id_new = user_id::text WHERE user_id IS NOT NULL")
    
    # Drop old column and rename new one
    op.drop_column('trips', 'user_id')
    op.alter_column('trips', 'user_id_new', new_column_name='user_id', nullable=False)
    
    # Step 4: Change users.id to String
    # First, remove the default value from id column using raw SQL (it depends on the sequence)
    # This must be done before dropping constraints
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT")
    
    # Drop constraints that reference users.id
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_constraint('users_username_key', 'users', type_='unique')
    op.drop_constraint('users_pkey', 'users', type_='primary')
    
    # Drop the sequence (no longer needed for String IDs) - now safe since default is removed
    op.execute("DROP SEQUENCE IF EXISTS users_id_seq")
    
    # Add new column
    op.add_column('users', sa.Column('id_new', sa.String(length=255), nullable=True))
    
    # Copy data (convert int to string) - this will be empty for fresh database
    op.execute("UPDATE users SET id_new = id::text WHERE id IS NOT NULL")
    
    # Drop old column and rename new one
    op.drop_column('users', 'id')
    op.alter_column('users', 'id_new', new_column_name='id', nullable=False)
    
    # Recreate primary key
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Recreate unique constraints
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    
    # Recreate foreign key (references users.id which is now String)
    op.create_foreign_key('trips_user_id_fkey', 'trips', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Revert migration (not recommended - data loss possible)."""
    # Revert foreign key
    op.drop_constraint('trips_user_id_fkey', 'trips', type_='foreignkey')
    
    # Revert trips.user_id to Integer
    op.add_column('trips', sa.Column('user_id_old', sa.Integer(), nullable=True))
    op.execute("UPDATE trips SET user_id_old = CAST(user_id AS INTEGER) WHERE user_id ~ '^[0-9]+$'")
    op.drop_column('trips', 'user_id')
    op.alter_column('trips', 'user_id_old', new_column_name='user_id', nullable=False)
    op.create_foreign_key('trips_user_id_fkey', 'trips', 'users', ['user_id'], ['id'])
    
    # Revert users.id to Integer
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_constraint('users_username_key', 'users', type_='unique')
    
    # Recreate sequence
    op.execute("CREATE SEQUENCE users_id_seq")
    op.execute("ALTER SEQUENCE users_id_seq OWNED BY users.id")
    
    op.add_column('users', sa.Column('id_old', sa.Integer(), server_default=sa.text("nextval('users_id_seq'::regclass)"), nullable=True))
    op.execute("UPDATE users SET id_old = CAST(id AS INTEGER) WHERE id ~ '^[0-9]+$'")
    op.drop_column('users', 'id')
    op.alter_column('users', 'id_old', new_column_name='id', nullable=False)
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    
    # Revert password_hash to NOT NULL
    op.alter_column('users', 'password_hash',
                   existing_type=sa.String(length=128),
                   nullable=False)
