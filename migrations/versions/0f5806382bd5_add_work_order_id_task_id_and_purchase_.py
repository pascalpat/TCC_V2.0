"""Add work_order_id, task_id, and purchase_order_id to entries_workers   

Revision ID: 0f5806382bd5
Revises: 24924b57509d
Create Date: 2025-01-02 23:26:03.196370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f5806382bd5'
down_revision = '24924b57509d'
branch_labels = None
depends_on = None


def upgrade():
    
    with op.batch_alter_table('entries_workers', schema=None) as batch_op:
        # 1) Add columns
        batch_op.add_column(sa.Column('work_order_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('task_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('purchase_order_id', sa.Integer(), nullable=True))

        # 2) Create foreign keys
        batch_op.create_foreign_key(
            'fk_entries_workers_work_order_id',
            'work_orders',
            ['work_order_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_entries_workers_task_id',
            'project_tasks',
            ['task_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_entries_workers_purchase_order_id',
            'purchase_orders',
            ['purchase_order_id'],
            ['id']
        )

def downgrade():
    with op.batch_alter_table('entries_workers', schema=None) as batch_op:
        batch_op.drop_constraint('fk_entries_workers_purchase_order_id', type_='foreignkey')
        batch_op.drop_constraint('fk_entries_workers_task_id', type_='foreignkey')
        batch_op.drop_constraint('fk_entries_workers_work_order_id', type_='foreignkey')

        batch_op.drop_column('purchase_order_id')
        batch_op.drop_column('task_id')
        batch_op.drop_column('work_order_id')
