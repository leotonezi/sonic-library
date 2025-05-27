"""add external book id to user books

Revision ID: cc15d9fb8e79
Revises: 455370611b67
Create Date: 2025-05-17 17:32:44.305599

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'cc15d9fb8e79'
down_revision = '455370611b67'
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


def unique_constraint_exists(table, constraint):
    """Helper function to check if a unique constraint exists"""
    bind = op.get_bind()
    inspector = inspect(bind)
    unique_constraints = [const['name'] for const in inspector.get_unique_constraints(table)]
    return constraint in unique_constraints


def foreign_key_exists(table, constraint):
    """Helper function to check if a foreign key exists"""
    bind = op.get_bind()
    inspector = inspect(bind)
    fks = [fk['name'] for fk in inspector.get_foreign_keys(table)]
    return constraint in fks


def upgrade() -> None:
    # Only proceed if external_book_id doesn't exist
    if not column_exists('user_books', 'external_book_id'):
        # Drop existing unique constraint if it exists
        if unique_constraint_exists('user_books', '_user_book_uc'):
            op.drop_constraint('_user_book_uc', 'user_books', type_='unique')

        # Drop the existing foreign key constraint if it exists
        if foreign_key_exists('user_books', 'user_books_book_id_fkey'):
            op.drop_constraint('user_books_book_id_fkey', 'user_books', type_='foreignkey')

        # Make book_id nullable
        op.alter_column('user_books', 'book_id',
                        existing_type=sa.Integer(),
                        nullable=True)

        # Add external_book_id column
        op.add_column('user_books',
            sa.Column('external_book_id', sa.String(), nullable=True)
        )

        # Add check constraint if it doesn't exist
        if not constraint_exists('user_books', 'check_one_book_reference'):
            op.create_check_constraint(
                'check_one_book_reference',
                'user_books',
                "(book_id IS NOT NULL AND external_book_id IS NULL) OR (book_id IS NULL AND external_book_id IS NOT NULL)"
            )

        # Add unique constraints if they don't exist
        if not unique_constraint_exists('user_books', '_user_book_uc'):
            op.create_unique_constraint(
                '_user_book_uc',
                'user_books',
                ['user_id', 'book_id']
            )
        
        if not unique_constraint_exists('user_books', '_user_external_book_uc'):
            op.create_unique_constraint(
                '_user_external_book_uc',
                'user_books',
                ['user_id', 'external_book_id']
            )

        # Re-add foreign key constraint
        if not foreign_key_exists('user_books', 'user_books_book_id_fkey'):
            op.create_foreign_key(
                'user_books_book_id_fkey',
                'user_books',
                'books',
                ['book_id'],
                ['id'],
                ondelete='CASCADE'
            )


def downgrade() -> None:
    # Only proceed if the column exists
    if column_exists('user_books', 'external_book_id'):
        # Drop constraints if they exist
        if constraint_exists('user_books', 'check_one_book_reference'):
            op.drop_constraint('check_one_book_reference', 'user_books', type_='check')
        
        if unique_constraint_exists('user_books', '_user_external_book_uc'):
            op.drop_constraint('_user_external_book_uc', 'user_books', type_='unique')
        
        if unique_constraint_exists('user_books', '_user_book_uc'):
            op.drop_constraint('_user_book_uc', 'user_books', type_='unique')

        # Drop the foreign key constraint if it exists
        if foreign_key_exists('user_books', 'user_books_book_id_fkey'):
            op.drop_constraint('user_books_book_id_fkey', 'user_books', type_='foreignkey')

        # Make book_id non-nullable again
        op.alter_column('user_books', 'book_id',
                        existing_type=sa.Integer(),
                        nullable=False)

        # Drop external_book_id column
        op.drop_column('user_books', 'external_book_id')

        # Re-add original constraints
        if not unique_constraint_exists('user_books', '_user_book_uc'):
            op.create_unique_constraint(
                '_user_book_uc',
                'user_books',
                ['user_id', 'book_id']
            )

        # Re-add foreign key constraint
        if not foreign_key_exists('user_books', 'user_books_book_id_fkey'):
            op.create_foreign_key(
                'user_books_book_id_fkey',
                'user_books',
                'books',
                ['book_id'],
                ['id'],
                ondelete='CASCADE'
            )