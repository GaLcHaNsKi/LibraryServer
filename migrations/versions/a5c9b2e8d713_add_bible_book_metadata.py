"""add Bible book abbreviations and display order

Revision ID: a5c9b2e8d713
Revises: c1a9e6f2b7d4
Create Date: 2026-10-06
"""

from alembic import op
import sqlalchemy as sa


revision = "a5c9b2e8d713"
down_revision = "c1a9e6f2b7d4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("bible_books", schema=None) as batch_op:
        batch_op.add_column(sa.Column("abbreviation", sa.String(length=20), nullable=True))
        batch_op.add_column(
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade():
    with op.batch_alter_table("bible_books", schema=None) as batch_op:
        batch_op.drop_column("sort_order")
        batch_op.drop_column("abbreviation")
