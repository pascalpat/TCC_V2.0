"""add date_of_report to MaterialEntry

Revision ID: 54d6fda2ba26
Revises: 98712e8649e0
Create Date: 2025-05-04 20:29:19.867229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54d6fda2ba26'
down_revision = '98712e8649e0'
branch_labels = None
depends_on = None


def upgrade():
    # Add the date_of_report column to the entries_material table
    op.add_column(
        'entries_material',
        sa.Column('date_of_report', sa.Date(), nullable=True)
    )
    # If you want to enforce NOT NULL going forward, you can
    # set a server_default or backfill existing rows, then:
    # op.alter_column('entries_material', 'date_of_report', nullable=False)

def downgrade():
    op.drop_column('entries_material', 'date_of_report')