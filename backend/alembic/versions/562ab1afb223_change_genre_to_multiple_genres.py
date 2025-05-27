"""change genre to multiple genres

Revision ID: 562ab1afb223
Revises: cc15d9fb8e79
Create Date: 2025-05-20 21:04:40.715569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '562ab1afb223'
down_revision: Union[str, None] = 'cc15d9fb8e79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Create genres table if not exists
    if 'genres' not in inspector.get_table_names():
        op.create_table(
            'genres',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String, unique=True, nullable=False),
        )

    # Create book_genres association table if not exists
    if 'book_genres' not in inspector.get_table_names():
        op.create_table(
            'book_genres',
            sa.Column('book_id', sa.Integer, sa.ForeignKey('books.id'), primary_key=True),
            sa.Column('genre_id', sa.Integer, sa.ForeignKey('genres.id'), primary_key=True),
        )

def downgrade():
    op.drop_table('book_genres')
    op.drop_table('genres')
