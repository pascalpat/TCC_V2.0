"""add metier and taux_horaire to entries_workers

Revision ID: 6f4a10b9a3cd
Revises: f431effa4856
Create Date: 2025-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '6f4a10b9a3cd'
down_revision = 'f431effa4856'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('entries_workers')}
    with op.batch_alter_table('entries_workers') as batch_op:
        if 'metier' not in columns:
            batch_op.add_column(sa.Column('metier', sa.String(length=100), nullable=True))
        if 'taux_horaire' not in columns:
            batch_op.add_column(sa.Column('taux_horaire', sa.Float(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {c['name'] for c in inspector.get_columns('entries_workers')}
    with op.batch_alter_table('entries_workers') as batch_op:
        if 'taux_horaire' in columns:
            batch_op.drop_column('taux_horaire')
        if 'metier' in columns:
            batch_op.drop_column('metier')