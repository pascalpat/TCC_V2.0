"""allow material_id nullable in entries_material

Revision ID: a422288fac32
Revises: 54d6fda2ba26
Create Date: 2025-05-04 20:51:19.259239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a422288fac32'
down_revision = '54d6fda2ba26'
branch_labels = None
depends_on = None


def upgrade():
   # This batch context will handle SQLite’s lack of ALTER-COLUMN support
    with op.batch_alter_table('entries_material') as batch_op:
        batch_op.alter_column(
            'material_id',
            existing_type=sa.Integer(),
            nullable=True
        )

def downgrade():
    with op.batch_alter_table('entries_material') as batch_op:
        batch_op.alter_column(
            'material_id',
            existing_type=sa.Integer(),
            nullable=False
        )