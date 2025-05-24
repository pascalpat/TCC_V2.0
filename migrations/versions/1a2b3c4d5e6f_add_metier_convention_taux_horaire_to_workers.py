"""Add metier, convention & taux_horaire to workers

Revision ID: 1a2b3c4d5e6f
Revises: 053f298e8086
Create Date: 2025-05-23 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '053f298e8086'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('workers') as batch_op:
        batch_op.add_column(sa.Column('metier',       sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('convention',   sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('taux_horaire', sa.Float(),            nullable=True))

def downgrade():
    with op.batch_alter_table('workers') as batch_op:
        batch_op.drop_column('taux_horaire')
        batch_op.drop_column('convention')
        batch_op.drop_column('metier')