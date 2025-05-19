"""add work_order_id to entries_daily_notes

Revision ID: 4470067a87bf
Revises: afe1bd2d9e19
Create Date: 2025-05-19 00:14:11.869309

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'XXXX'
down_revision = 'afe1bd2d9e19'
branch_labels = None
depends_on = None

def upgrade():
    # add the FK column
    op.add_column(
        'entries_daily_notes',
        sa.Column('work_order_id', sa.Integer(), sa.ForeignKey('work_orders.id'), nullable=True)
    )
       