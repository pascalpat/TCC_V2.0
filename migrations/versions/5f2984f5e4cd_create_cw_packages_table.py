"""create cw_packages table

Revision ID: 5f2984f5e4cd
Revises: 810d1f60dd63
Create Date: 2025-04-23 19:39:13.021623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f2984f5e4cd'
down_revision = '810d1f60dd63'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'cw_packages',
        sa.Column('code', sa.String(length=50), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
    )

def downgrade():
    op.drop_table('cw_packages')