"""track creation time for admin dashboard charts

Revision ID: e2a4d1c9f725
Revises: a5c9b2e8d713
Create Date: 2026-10-22
"""
from alembic import op
import sqlalchemy as sa


revision = "e2a4d1c9f725"
down_revision = "a5c9b2e8d713"
branch_labels = None
depends_on = None


def upgrade():
    # Existing records have no reliable creation date in the old schema, so
    # keep it empty instead of inventing a date. New records receive it from
    # the SQLAlchemy model defaults.
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.create_index("ix_users_created_at", "users", ["created_at"])
    op.add_column("libraries", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.create_index("ix_libraries_created_at", "libraries", ["created_at"])
    op.add_column("books", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.create_index("ix_books_created_at", "books", ["created_at"])


def downgrade():
    op.drop_index("ix_books_created_at", table_name="books")
    op.drop_column("books", "created_at")
    op.drop_index("ix_libraries_created_at", table_name="libraries")
    op.drop_column("libraries", "created_at")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_column("users", "created_at")
