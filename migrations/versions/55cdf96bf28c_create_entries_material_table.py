"""Create entries_material table

Revision ID: 55cdf96bf28c
Revises: 2c3108ef5e57
Create Date: 2025-01-01 20:02:49.737271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55cdf96bf28c'
down_revision = '2c3108ef5e57'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'entries_material',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=True),
        sa.Column('activity_code_id', sa.Integer(), sa.ForeignKey('activity_codes.id'), nullable=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('project_tasks.id'), nullable=True),
        sa.Column('work_order_id', sa.Integer(), sa.ForeignKey('work_orders.id'), nullable=True),
        sa.Column('material_name', sa.String(255), nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=True),
        sa.Column('quantity_used', sa.Float(), nullable=True),
        sa.Column('supplier_name', sa.String(255), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('procurement_status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    # No separate op.create_foreign_key calls needed for a new table in SQLite.


def downgrade():
    op.drop_table('entries_material')