"""Create work_order_entries table

Revision ID: <some_hash>
Revises: 1f77c651f661  # or whatever your current head is
Create Date: 2025-01-02 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '640d03a9974f' #create work_order_entries table and attachements table
down_revision = '1f77c651f661'  # matches your current head
branch_labels = None
depends_on = None

def upgrade():
    # 1) Create work_order_entries
    op.create_table(
        'work_order_entries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # Foreign Keys
        sa.Column('work_order_id',    sa.Integer(), sa.ForeignKey('work_orders.id'),  nullable=False),
        sa.Column('worker_id',        sa.Integer(), sa.ForeignKey('workers.id'),      nullable=True),
        sa.Column('project_id',       sa.Integer(), sa.ForeignKey('projects.id'),     nullable=False),
        sa.Column('task_id',          sa.Integer(), sa.ForeignKey('project_tasks.id'), nullable=True),
        sa.Column('activity_code_id', sa.Integer(), sa.ForeignKey('activity_codes.id'), nullable=False),

        # Basic Fields
        sa.Column('hours_worked',  sa.Float(),   nullable=True, server_default='0'),
        sa.Column('date',          sa.Date(),    nullable=True),
        sa.Column('description',   sa.Text(),    nullable=True),

        # Costs
        sa.Column('labor_cost',          sa.Float(), nullable=True, server_default='0'),
        sa.Column('equipement_cost',     sa.Float(), nullable=True, server_default='0'),
        sa.Column('subcontractor_cost',  sa.Float(), nullable=True, server_default='0'),
        sa.Column('service_cost',        sa.Float(), nullable=True, server_default='0'),
        sa.Column('total_cost',          sa.Float(), nullable=True, server_default='0'),
        sa.Column('progress_percentage', sa.Float(), nullable=True, server_default='0'),

        # Timestamps / Auditing
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
    )

    # 2) Create work_order_entry_attachments
    op.create_table(
        'work_order_entry_attachments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        # Link each attachment to a specific entry:
        sa.Column('entry_id',    sa.Integer(), sa.ForeignKey('work_order_entries.id'), nullable=False),

        # File info
        sa.Column('file_path',   sa.String(255), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('doc_type',    sa.String(50),  nullable=True),

        # Possibly track upload time
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    # Drop in reverse dependency order
    op.drop_table('work_order_entry_attachments')
    op.drop_table('work_order_entries')