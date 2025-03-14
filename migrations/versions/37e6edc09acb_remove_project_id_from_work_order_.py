"""Remove project_id from work_order_entries

Revision ID: 37e6edc09acb
Revises: 0f5806382bd5
Create Date: 2025-01-02 23:54:53.069257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37e6edc09acb'
down_revision = '0f5806382bd5'
branch_labels = None
depends_on = None


def upgrade():
   with op.batch_alter_table('work_order_entries', schema=None) as batch_op:
        # Just drop the column. In SQLite batch mode, 
        # this also removes any FK referencing it.
        batch_op.drop_column('project_id')

def downgrade():
    with op.batch_alter_table('work_order_entries', schema=None) as batch_op:
        # Re-add the column and its FK to projects
        batch_op.add_column(sa.Column('project_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_work_order_entries_project_id',
            'projects',
            ['project_id'],
            ['id']
        )