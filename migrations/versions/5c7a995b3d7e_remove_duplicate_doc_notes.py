"""remove duplicate doc_notes column if present

Revision ID: 5c7a995b3d7e
Revises: 4ab0aa99c24f
Create Date: 2025-05-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '5c7a995b3d7e'
down_revision = '4ab0aa99c24f'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'doc_notes_1' in columns:
            batch_op.drop_column('doc_notes_1')


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'doc_notes_1' not in columns:
            batch_op.add_column(sa.Column('doc_notes_1', sa.Text(), nullable=True))
