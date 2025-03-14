"""Rebuild payment_items table

Revision ID: cead19b745e5
Revises: 210d6b2a1c27
Create Date: 2025-01-07 16:55:01.360687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cead19b745e5'
down_revision = '210d6b2a1c27'
branch_labels = None
depends_on = None


def upgrade():
    """
        In this migration we want to:
      1) Make `activity_codes.project_id` nullable.
      2) Make `materials.purchase_order_id` nullable and allow `materials.created_at` to be nullable.
      3) Remove `default_activity_code_id` column from `payment_items`.
      4) Remove `payment_item_id` column from `project_tasks`.
      5) Remove `material_id` column from `purchase_orders`.
    """

    # 1) Make activity_codes.project_id nullable
    with op.batch_alter_table('activity_codes', schema=None) as batch_op:
        batch_op.alter_column(
            'project_id',
            existing_type=sa.INTEGER(),
            nullable=True
        )

    # 2) Make materials.purchase_order_id nullable & allow materials.created_at to be nullable
    with op.batch_alter_table('materials', schema=None) as batch_op:
        batch_op.alter_column(
            'purchase_order_id',
            existing_type=sa.INTEGER(),
            nullable=True
        )
        batch_op.alter_column(
            'created_at',
            existing_type=sa.DateTime(),
            nullable=True
        )

    # 3) Drop `default_activity_code_id` from payment_items
    #    (which also removes its unnamed FK on SQLite).
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        # If Alembic auto-generated `drop_constraint(None, ...)`, remove or comment that out.
        # We'll rely on dropping the column to drop the FK in SQLite.
        batch_op.drop_column('default_activity_code_id')

    # 4) Drop payment_item_id from project_tasks
    #    (which also removes its unnamed FK in SQLite).
    with op.batch_alter_table('project_tasks', schema=None) as batch_op:
        batch_op.drop_column('payment_item_id')

    # 5) Drop material_id from purchase_orders
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        batch_op.drop_column('material_id')


def downgrade():
    """
    Reverse the above changes:
      1) Revert activity_codes.project_id to NOT NULL.
      2) Revert materials.purchase_order_id and created_at to NOT NULL.
      3) Re-add default_activity_code_id on payment_items with a new FK.
      4) Re-add payment_item_id on project_tasks with a new FK.
      5) Re-add material_id on purchase_orders with a new FK.
    """

    # 5) Re-add material_id to purchase_orders
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('material_id', sa.String(length=100), nullable=True))
        batch_op.create_foreign_key(
            'fk_purchase_orders_material_id',
            'materials',
            ['material_id'], ['material_id'],
            ondelete='SET NULL'
        )

    # 4) Re-add payment_item_id to project_tasks
    with op.batch_alter_table('project_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_item_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_project_tasks_payment_item_id',
            'payment_items',
            ['payment_item_id'], ['id']
        )

    # 3) Re-add default_activity_code_id to payment_items
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('default_activity_code_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_payment_items_default_activity_code_id',
            'activity_codes',
            ['default_activity_code_id'], ['id']
        )

    # 2) Revert materials columns to NOT NULL
    with op.batch_alter_table('materials', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=sa.DateTime(),
            nullable=False
        )
        batch_op.alter_column(
            'purchase_order_id',
            existing_type=sa.INTEGER(),
            nullable=False
        )

    # 1) Revert activity_codes.project_id to NOT NULL
    with op.batch_alter_table('activity_codes', schema=None) as batch_op:
        batch_op.alter_column(
            'project_id',
            existing_type=sa.INTEGER(),
            nullable=False
        )