"""Create entries_equipment table

Revision ID: 2c3108ef5e57
Revises: d25a0182c9c7
Create Date: 2025-01-01 19:37:47.391015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c3108ef5e57'
down_revision = 'd25a0182c9c7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'entries_equipment',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('date_of_report', sa.Date(), nullable=False, index=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('equipment_id', sa.Integer(), sa.ForeignKey('equipment.id'), nullable=False),
        sa.Column('hours_used', sa.Float(), nullable=False, server_default='0'),
        sa.Column('activity_id', sa.Integer(), sa.ForeignKey('activity_codes.id'), nullable=True),
        sa.Column('cwp', sa.String(50), nullable=True),
        sa.Column('phase', sa.String(50), nullable=True),
        sa.Column('usage_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade():
     op.drop_table('entries_equipment')
