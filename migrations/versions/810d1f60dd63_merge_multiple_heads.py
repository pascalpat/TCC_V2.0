"""Merge multiple heads

Revision ID: 810d1f60dd63
Revises: 5c9128ba1ba0, a87f3c0b5e8c, d0bba7d7687b
Create Date: 2025-04-22 22:32:27.753789

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '810d1f60dd63'
down_revision = ('5c9128ba1ba0', 'a87f3c0b5e8c', 'd0bba7d7687b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
