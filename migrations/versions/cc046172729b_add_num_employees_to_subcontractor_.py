"""add num_employees to subcontractor_entries

Revision ID: cc046172729b
Revises: 6f4a10b9a3cd
Create Date: 2025-05-31 13:43:10.864206

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'cc046172729b'
down_revision = '6f4a10b9a3cd'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('subcontractor_entries')}
    with op.batch_alter_table('subcontractor_entries') as batch_op:
        if 'num_employees' not in columns:
            batch_op.add_column(sa.Column('num_employees', sa.Integer(), nullable=True, server_default='0'))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('subcontractor_entries')}
    with op.batch_alter_table('subcontractor_entries') as batch_op:
        if 'num_employees' in columns:
            batch_op.drop_column('num_employees')