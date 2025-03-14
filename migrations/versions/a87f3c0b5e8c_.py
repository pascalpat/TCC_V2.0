"""empty message

Revision ID: a87f3c0b5e8c
Revises: aa86ddf8cd47
Create Date: 2025-01-07 19:53:57.201320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a87f3c0b5e8c'
down_revision = 'aa86ddf8cd47'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Add the new column as nullable=True with a default
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'project_id',
                sa.Integer(),
                nullable=True,
                server_default='1'  # or some valid project ID if you have a "dummy" Project row
            )
        )
        batch_op.create_foreign_key(
            'fk_payment_items_project_id',
            'projects',
            ['project_id'],
            ['id']
        )

    # 2) Now that existing rows were copied successfully, we can remove the default
    #    and make the column non-null:
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        # remove server_default so new inserts won't automatically get "1"
        batch_op.alter_column(
            'project_id',
            server_default=None,
            existing_type=sa.Integer(),
            nullable=False
        )

def downgrade():
    with op.batch_alter_table('payment_items', schema=None) as batch_op:
        # drop the FK constraint by name
        batch_op.drop_constraint('fk_payment_items_project_id', type_='foreignkey')
        batch_op.drop_column('project_id')
