"""add project_id to cw_packages

Revision ID: 98712e8649e0
Revises: faac170c1e01
Create Date: 2025-04-23 20:48:30.725267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98712e8649e0'
down_revision = 'faac170c1e01'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add project_id with a default so existing rows aren’t NULL
    op.add_column(
        'cw_packages',
        sa.Column('project_id',
                  sa.String(length=50),
                  nullable=False,
                  server_default='DEFAULT_PROJECT')
    )
    op.create_index(
        'ix_cw_packages_project_id',
        'cw_packages',
        ['project_id']
    )

def downgrade():
    op.drop_index('ix_cw_packages_project_id', table_name='cw_packages')
    op.drop_column('cw_packages', 'project_id')
