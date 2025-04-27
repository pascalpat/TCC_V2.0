"""add default_unit to cw_packages

Revision ID: faac170c1e01
Revises: 5f2984f5e4cd
Create Date: 2025-04-23 19:55:10.922080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'faac170c1e01'
down_revision = '5f2984f5e4cd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cw_packages', sa.Column('default_unit', sa.String(length=20), nullable=True))

def downgrade():
    op.drop_column('cw_packages', 'default_unit')
