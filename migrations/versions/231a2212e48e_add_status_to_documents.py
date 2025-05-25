"""add_status-to_docuements.py

Revision ID: 2b9ddba5022f
Revises: 1a2b3c4d5e6f
Create Date: 2025-05-24 17:37:05.164396

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '2b9ddba5022f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


record_status = sa.Enum('pending', 'committed', name='record_status')


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    # Ensure the enum exists for databases that require explicit creation
    record_status.create(bind, checkfirst=True)
    with op.batch_alter_table('documents') as batch_op:
        if 'status' not in columns:
            batch_op.add_column(sa.Column('status', record_status, nullable=True))

def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'status' in columns:
            batch_op.drop_column('status')
            