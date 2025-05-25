"""add doc_notes_to_documents

Revision ID: 4ab0aa99c24f
Revises: 2b9ddba5022f
Create Date: 2025-05-24 20:32:42.571729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ab0aa99c24f'
down_revision = '2b9ddba5022f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('documents', sa.Column('doc_notes', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('documents', 'doc_notes')