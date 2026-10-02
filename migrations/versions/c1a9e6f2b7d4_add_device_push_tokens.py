"""add FCM device push tokens

Revision ID: c1a9e6f2b7d4
Revises: fe9d4c3b2a10
Create Date: 2026-10-02
"""
from alembic import op
import sqlalchemy as sa


revision = 'c1a9e6f2b7d4'
down_revision = 'fe9d4c3b2a10'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'device_push_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_device_push_tokens_user_id', 'device_push_tokens', ['user_id'])


def downgrade():
    op.drop_index('ix_device_push_tokens_user_id', table_name='device_push_tokens')
    op.drop_table('device_push_tokens')
