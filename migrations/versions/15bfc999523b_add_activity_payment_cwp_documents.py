"""add activity, payment item, cwp to documents

Revision ID: 15bfc999523b
Revises: 5c7a995b3d7e
Create Date: 2025-05-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '15bfc999523b'
down_revision = '5c7a995b3d7e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'activity_id' not in columns:
            batch_op.add_column(sa.Column('activity_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(None, 'activity_codes', ['activity_id'], ['id'])
        if 'payment_item_id' not in columns:
            batch_op.add_column(sa.Column('payment_item_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(None, 'payment_items', ['payment_item_id'], ['id'])
        if 'cwp' not in columns:
            batch_op.add_column(sa.Column('cwp', sa.String(length=50), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('documents')}
    with op.batch_alter_table('documents') as batch_op:
        if 'cwp' in columns:
            batch_op.drop_column('cwp')
        if 'payment_item_id' in columns:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_column('payment_item_id')
        if 'activity_id' in columns:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_column('activity_id')