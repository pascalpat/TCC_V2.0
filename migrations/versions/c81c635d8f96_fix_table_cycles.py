"""Fix table cycles

Revision ID: c81c635d8f96
Revises: 51b43ac9c130
Create Date: 2025-01-01 12:49:24.749242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c81c635d8f96'
down_revision = '51b43ac9c130'
branch_labels = None
depends_on = None

def upgrade():
    # Update the activity_codes table
    with op.batch_alter_table('activity_codes', schema=None) as batch_op:
        # Drop task_id column
        batch_op.drop_column('task_id')  # Only drop the column since the constraint doesn't exist in SQLite

    # Update the purchase_orders table
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        # Drop activity_code_id column and any associated constraints
        batch_op.drop_column('activity_code_id')

def downgrade():
    # Revert changes to the purchase_orders table
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        # Add activity_code_id column back
        batch_op.add_column(sa.Column('activity_code_id', sa.INTEGER(), nullable=True))
        # Create foreign key constraint (replace `None` with the correct name if needed)
        batch_op.create_foreign_key('fk_purchase_orders_activity_codes', 'activity_codes', ['activity_code_id'], ['id'])

    # Revert changes to the activity_codes table
    with op.batch_alter_table('activity_codes', schema=None) as batch_op:
        # Add task_id column back
        batch_op.add_column(sa.Column('task_id', sa.INTEGER(), nullable=True))
        # Create foreign key constraint (replace `None` with the correct name if needed)
        batch_op.create_foreign_key('fk_activity_codes_project_tasks', 'project_tasks', ['task_id'], ['id'])
