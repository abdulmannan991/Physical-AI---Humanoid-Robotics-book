"""Add authentication tables and user linking

Revision ID: 001_add_authentication
Revises:
Create Date: 2025-12-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Revision identifiers
revision = '001_add_authentication'
down_revision = None  # This is the first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration: Create users table and link to chat_sessions."""

    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('username', sa.Text(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('profile_image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),

        # Constraints
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.CheckConstraint('LENGTH(password_hash) > 0', name='ck_users_password_hash_not_empty'),

        # Table comment
        comment='User accounts with authentication credentials'
    )

    # 2. Create indexes on users table
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    op.create_index('idx_users_created_at', 'users', ['created_at'], postgresql_using='btree')

    # 3. Add user_id column to chat_sessions (nullable for backward compatibility)
    op.add_column(
        'chat_sessions',
        sa.Column('user_id', UUID(as_uuid=True), nullable=True)
    )

    # 4. Create foreign key constraint
    op.create_foreign_key(
        'fk_chat_sessions_user_id',
        'chat_sessions',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 5. Create index on user_id for fast lookups
    op.create_index('idx_chat_sessions_user_id', 'chat_sessions', ['user_id'])


def downgrade() -> None:
    """Rollback migration: Remove users table and user_id from chat_sessions."""

    # 1. Drop index on chat_sessions.user_id
    op.drop_index('idx_chat_sessions_user_id', table_name='chat_sessions')

    # 2. Drop foreign key constraint
    op.drop_constraint('fk_chat_sessions_user_id', 'chat_sessions', type_='foreignkey')

    # 3. Drop user_id column from chat_sessions
    op.drop_column('chat_sessions', 'user_id')

    # 4. Drop indexes on users table
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')

    # 5. Drop users table
    op.drop_table('users')
