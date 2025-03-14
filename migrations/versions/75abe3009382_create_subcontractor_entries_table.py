"""Create subcontractor_entries table

Revision ID: 75abe3009382
Revises: 55cdf96bf28c
Create Date: 2025-01-01 20:23:55.167914

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '75abe3009382'
down_revision = '55cdf96bf28c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'subcontractor_entries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # Inline foreign keys:
        sa.Column('subcontractor_id', sa.Integer(), sa.ForeignKey('subcontractors.id'), nullable=False),
        sa.Column('project_id',       sa.Integer(), sa.ForeignKey('projects.id'),       nullable=False),
        sa.Column('task_id',          sa.Integer(), sa.ForeignKey('project_tasks.id'),  nullable=True),
        sa.Column('work_order_id',    sa.Integer(), sa.ForeignKey('work_orders.id'),    nullable=True),

        sa.Column('date',                sa.Date(),    nullable=True),
        sa.Column('description',         sa.Text(),    nullable=True),
        sa.Column('equipment_hours',     sa.Float(),   server_default='0'),
        sa.Column('material_cost',       sa.Float(),   server_default='0'),
        sa.Column('labor_hours',         sa.Float(),   server_default='0'),
        sa.Column('total_cost',          sa.Float(),   server_default='0'),
        sa.Column('progress_percentage', sa.Float(),   server_default='0'),
        sa.Column('created_at',          sa.DateTime(), nullable=True),
        sa.Column('updated_at',          sa.DateTime(), nullable=True),
    )
    # No separate create_foreign_key calls needed for a brand-new table in SQLite.


def downgrade():
    op.drop_table('subcontractor_entries')
