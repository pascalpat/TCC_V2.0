"""Add columns to work_orders & drop work_order_entries table

Revision ID: 86ac237724e8
Revises: 37e6edc09acb
Create Date: 2025-01-03 23:24:08.815383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86ac237724e8'
down_revision = '37e6edc09acb'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Add new columns to 'work_orders'
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        # Example columns - adjust names/types as you prefer:

        batch_op.add_column(sa.Column('owner_wo_number', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('scope_of_work', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('pricing_type', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('owner_signature_url', sa.String(2083), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by', sa.Integer(), nullable=True))
        # If you prefer them to be VARCHAR, just use sa.String(50), etc.

    # 2) Drop the 'work_order_entries' table
    op.drop_table('work_order_entries')


def downgrade():
    # Reverse the operations

    # 1) Recreate 'work_order_entries' table
    op.create_table(
        'work_order_entries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('work_order_id', sa.Integer(), nullable=False),
        sa.Column('worker_id', sa.Integer(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('activity_code_id', sa.Integer(), nullable=False),
        sa.Column('hours_worked', sa.Float(), nullable=True, server_default='0'),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('labor_cost', sa.Float(), nullable=True, server_default='0'),
        sa.Column('equipement_cost', sa.Float(), nullable=True, server_default='0'),
        sa.Column('subcontractor_cost', sa.Float(), nullable=True, server_default='0'),
        sa.Column('service_cost', sa.Float(), nullable=True, server_default='0'),
        sa.Column('total_cost', sa.Float(), nullable=True, server_default='0'),
        sa.Column('progress_percentage', sa.Float(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        # ForeignKey constraints can be re-added if needed:
        # sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ),
        # ...
    )

    # 2) Drop the newly added columns from 'work_orders'
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        batch_op.drop_column('owner_wo_number')
        batch_op.drop_column('scope_of_work')
        batch_op.drop_column('pricing_type')
        batch_op.drop_column('owner_signature_url')
        batch_op.drop_column('created_by')
        batch_op.drop_column('updated_by')