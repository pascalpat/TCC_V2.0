"""Add columns to EquipmentEntry

Revision ID: 24924b57509d
Revises: ac2a68c3a9f2
Create Date: 2025-01-02 23:04:49.585708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24924b57509d'
down_revision = 'ac2a68c3a9f2'
branch_labels = None
depends_on = None


def upgrade():
   
 with op.batch_alter_table('entries_equipment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('work_order_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('task_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('purchase_order_id', sa.Integer(), nullable=True))

        batch_op.create_foreign_key(
            'fk_entries_equipment_work_order_id',
            'work_orders',
            ['work_order_id'], 
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_entries_equipment_task_id',
            'project_tasks',
            ['task_id'], 
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_entries_equipment_purchase_order_id',
            'purchase_orders',
            ['purchase_order_id'],
            ['id']
        )

def downgrade():
    with op.batch_alter_table('entries_equipment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_entries_equipment_purchase_order_id', type_='foreignkey')
        batch_op.drop_constraint('fk_entries_equipment_task_id', type_='foreignkey')
        batch_op.drop_constraint('fk_entries_equipment_work_order_id', type_='foreignkey')

        batch_op.drop_column('purchase_order_id')
        batch_op.drop_column('task_id')
        batch_op.drop_column('work_order_id')