"""add_status-to_docuements.py

Revision ID: 2b9ddba5022f
Revises: 1a2b3c4d5e6f
Create Date: 2025-05-24 17:37:05.164396

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b9ddba5022f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


record_status = sa.Enum('pending', 'committed', name='record_status')


def upgrade():
    # Ensure the enum exists for databases that require explicit creation
    record_status.create(op.get_bind(), checkfirst=True)
    with op.batch_alter_table('documents') as batch_op:
        batch_op.add_column(sa.Column('status', record_status, nullable=True))


def downgrade():
    with op.batch_alter_table('documents') as batch_op:
        batch_op.drop_column('status')
