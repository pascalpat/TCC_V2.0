"""add payment_item_id and cwp to entries_daily_notes

Revision ID: afe1bd2d9e19
Revises: 9e50e439e3b2
Create Date: 2025-05-18 20:05:01.427383

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'afe1bd2d9e19'
down_revision = '9e50e439e3b2'   # keep whatever value was already here
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('entries_daily_notes') as batch_op:
        batch_op.add_column(sa.Column('payment_item_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('cwp', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key(
            'fk_entries_daily_notes_payment_item_id',
            'payment_items',
            ['payment_item_id'],
            ['id']
        )

def downgrade():
    with op.batch_alter_table('entries_daily_notes') as batch_op:
        batch_op.drop_constraint('fk_entries_daily_notes_payment_item_id', type_='foreignkey')
        batch_op.drop_column('cwp')
        batch_op.drop_column('payment_item_id')