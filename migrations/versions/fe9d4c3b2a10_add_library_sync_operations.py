"""add idempotency records for offline library mutations

Revision ID: fe9d4c3b2a10
Revises: d611b5c4e31e
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa


revision = 'fe9d4c3b2a10'
down_revision = 'd611b5c4e31e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'library_sync_operations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('library_id', sa.Integer(), nullable=False),
        sa.Column('operation_id', sa.String(length=36), nullable=False),
        sa.Column('operation_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['library_id'], ['libraries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('library_id', 'operation_id')
    )


def downgrade():
    op.drop_table('library_sync_operations')
