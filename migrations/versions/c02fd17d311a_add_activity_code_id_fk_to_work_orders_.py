"""Add activity_code_id FK to work_orders referencing activity_codes

Revision ID: c02fd17d311a
Revises: 86ac237724e8
Create Date: 2025-01-03 23:43:51.288739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c02fd17d311a'
down_revision = '86ac237724e8'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Add a numeric column to reference 'activity_codes.id'
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activity_code_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_work_orders_activity_code_id',    # name of the FK constraint
            'activity_codes',                     # referenced table
            ['activity_code_id'],                 # local col
            ['id'],                               # remote col
            ondelete='SET NULL'                   # or 'CASCADE' / 'RESTRICT' if you prefer
        )

    # 2) (Optional) Drop the old 'activity_code' column if you don't need it anymore
    #    If you'd like to keep it for reference, just comment this out.
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        batch_op.drop_column('activity_code')


def downgrade():
    # Reverse the operations
    # 1) Re-add the old 'activity_code' column (if we dropped it)
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activity_code', sa.String(50), nullable=True))

    # 2) Drop the new FK and column
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_work_orders_activity_code_id', type_='foreignkey')
        batch_op.drop_column('activity_code_id')