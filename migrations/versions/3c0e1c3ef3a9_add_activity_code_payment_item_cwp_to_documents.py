"""add activity_code_id, payment_item_id, cwp_code to documents

Revision ID: 3c0e1c3ef3a9
Revises: 5c7a995b3d7e
Create Date: 2025-05-31 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '3c0e1c3ef3a9'
down_revision = '5c7a995b3d7e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'activity_code_id' not in columns:
            batch_op.add_column(sa.Column('activity_code_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(None, 'activity_codes', ['activity_code_id'], ['id'])
        if 'payment_item_id' not in columns:
            batch_op.add_column(sa.Column('payment_item_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(None, 'payment_items', ['payment_item_id'], ['id'])
        if 'cwp_code' not in columns:
            batch_op.add_column(sa.Column('cwp_code', sa.String(length=50), nullable=True))
            batch_op.create_foreign_key(None, 'cw_packages', ['cwp_code'], ['code'])


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'cwp_code' in columns:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_column('cwp_code')
        if 'payment_item_id' in columns:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_column('payment_item_id')
        if 'activity_code_id' in columns:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_column('activity_code_id')