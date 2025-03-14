"""Add entries_workers table

Revision ID: 2912bc5d2a06
Revises: c81c635d8f96
Create Date: 2025-01-01 13:34:03.031388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2912bc5d2a06'
down_revision = 'c81c635d8f96'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure no leftover temporary tables exist
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_activity_codes")
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_payment_items")

    # 1. Modify activity_codes
    with op.batch_alter_table('activity_codes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('task_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_activity_codes_task_id',
            'project_tasks',
            ['task_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_foreign_key(
            'fk_activity_codes_project_id',
            'projects',
            ['project_id'],
            ['id'],
            ondelete='CASCADE'
        )

    # 2. Make purchase_order_id on materials non-nullable
    with op.batch_alter_table('materials', schema=None) as batch_op:
        # Fill in at least one valid purchase_order_id if it's null
        op.execute("""
            UPDATE materials
            SET purchase_order_id = (
                SELECT id FROM purchase_orders LIMIT 1
            )
            WHERE purchase_order_id IS NULL
        """)
        batch_op.alter_column(
            'purchase_order_id',
            existing_type=sa.INTEGER(),
            nullable=False
        )

    # 3. Add activity_code_id, task_id to payment_items
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activity_code_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('task_id', sa.Integer(), nullable=True))

    # Populate activity_code_id with something valid
    op.execute("""
        UPDATE payment_items
        SET activity_code_id = (
            SELECT id FROM activity_codes LIMIT 1
        )
        WHERE activity_code_id IS NULL
    """)

    # Now make activity_code_id non-nullable & add FKs
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        batch_op.alter_column('activity_code_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            'fk_payment_items_task_id',
            'project_tasks',
            ['task_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_payment_items_activity_code_id',
            'activity_codes',
            ['activity_code_id'],
            ['id']
        )

    # 4. Add activity_code_id to project_tasks (in two steps)
    # Step A: Add the column as nullable
    with op.batch_alter_table('project_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activity_code_id', sa.Integer(), nullable=True))

    # Step B: Populate the new column with a valid default
    op.execute("""
        UPDATE project_tasks
        SET activity_code_id = (
            SELECT id FROM activity_codes LIMIT 1
        )
        WHERE activity_code_id IS NULL
    """)

    # Step C: Now make it non-nullable and add a foreign key
    with op.batch_alter_table('project_tasks', schema=None) as batch_op:
        batch_op.alter_column('activity_code_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            'fk_project_tasks_activity_code_id',
            'activity_codes',
            ['activity_code_id'],
            ['id']
        )

    # 5. Purchase_orders constraint changes
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        # Drop old unnamed constraint, then recreate it
        #batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_purchase_orders_material_id',
            'materials',
            ['material_id'],
            ['material_id'],
            ondelete='SET NULL'
        )


def downgrade():
    # Revert purchase_orders
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_purchase_orders_material_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_purchase_orders_old_constraint',
            'materials',
            ['material_id'],
            ['material_id']
        )
    
    # Revert project_tasks
    with op.batch_alter_table('project_tasks', schema=None) as batch_op:
        batch_op.drop_constraint('fk_project_tasks_activity_code_id', type_='foreignkey')
        batch_op.drop_column('activity_code_id')

    # Revert payment_items
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        batch_op.drop_constraint('fk_payment_items_activity_code_id', type_='foreignkey')
        batch_op.drop_constraint('fk_payment_items_task_id', type_='foreignkey')
        batch_op.drop_column('task_id')
        batch_op.drop_column('activity_code_id')

    # Revert materials
    with op.batch_alter_table('materials', schema=None) as batch_op:
        batch_op.alter_column(
            'purchase_order_id',
            existing_type=sa.INTEGER(),
            nullable=True
        )

    # Revert activity_codes
    with op.batch_alter_table('activity_codes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_activity_codes_project_id', type_='foreignkey')
        batch_op.drop_constraint('fk_activity_codes_task_id', type_='foreignkey')
        batch_op.drop_column('task_id')