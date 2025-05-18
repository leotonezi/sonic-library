"""add external book id to reviews

Revision ID: 455370611b67
Revises: 1d0cb44492c8
Create Date: 2025-05-17 12:51:22.931939

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '455370611b67'
down_revision = '1d0cb44492c8'
branch_labels = None
depends_on = None


def column_exists(table, column):
    """Helper function to check if a column exists"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table)]
    return column in columns


def constraint_exists(table, constraint):
    """Helper function to check if a constraint exists"""
    bind = op.get_bind()
    inspector = inspect(bind)
    constraints = [const['name'] for const in inspector.get_check_constraints(table)]
    return constraint in constraints


def upgrade() -> None:
    # Check if external_book_id column already exists
    if not column_exists('reviews', 'external_book_id'):
        # Drop the existing foreign key constraint if it exists
        try:
            op.drop_constraint('reviews_book_id_fkey', 'reviews', type_='foreignkey')
        except Exception:
            pass  # Constraint might not exist

        # Make book_id nullable
        op.alter_column('reviews', 'book_id',
                        existing_type=sa.Integer(),
                        nullable=True)

        # Add external_book_id column
        op.add_column('reviews',
            sa.Column('external_book_id', sa.String(), nullable=True)
        )

        # Add check constraint if it doesn't exist
        if not constraint_exists('reviews', 'check_one_book_reference'):
            op.create_check_constraint(
                'check_one_book_reference',
                'reviews',
                "(book_id IS NOT NULL AND external_book_id IS NULL) OR (book_id IS NULL AND external_book_id IS NOT NULL)"
            )

        # Re-add foreign key constraint
        op.create_foreign_key(
            'reviews_book_id_fkey',
            'reviews',
            'books',
            ['book_id'],
            ['id']
        )


def downgrade() -> None:
    # Only perform downgrade operations if the column exists
    if column_exists('reviews', 'external_book_id'):
        # Drop the check constraint if it exists
        try:
            op.drop_constraint('check_one_book_reference', 'reviews', type_='check')
        except Exception:
            pass  # Constraint might not exist

        # Drop the foreign key constraint
        try:
            op.drop_constraint('reviews_book_id_fkey', 'reviews', type_='foreignkey')
        except Exception:
            pass  # Constraint might not exist

        # Make book_id non-nullable again
        op.alter_column('reviews', 'book_id',
                        existing_type=sa.Integer(),
                        nullable=False)

        # Drop external_book_id column
        op.drop_column('reviews', 'external_book_id')

        # Re-add foreign key constraint
        op.create_foreign_key(
            'reviews_book_id_fkey',
            'reviews',
            'books',
            ['book_id'],
            ['id']
        )