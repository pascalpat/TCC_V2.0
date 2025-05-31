"""update entry status enums

Revision ID: c3c3c07dcbf6
Revises: cc046172729b
Create Date: 2025-05-31 15:15:23.469666

"""
from alembic import op
import sqlalchemy as sa

new_status = sa.Enum('pending', 'committed', 'rejected', name='entry_progress_status_new')
old_status = sa.Enum('pending', 'in_progress', 'completed', name='entry_progress_status')


# revision identifiers, used by Alembic.
revision = 'c3c3c07dcbf6'
down_revision = 'cc046172729b'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    tables = [
        'entries_material',
        'entries_equipment',
        'work_order_entries',
        'entries_workers',
        'subcontractor_entries'
    ]

    if bind.dialect.name == 'sqlite':
        for table in tables:
            op.execute(sa.text(f"UPDATE {table} SET status='committed' WHERE status='completed'"))
            op.execute(sa.text(f"UPDATE {table} SET status='pending' WHERE status='in_progress'"))
        return

    new_status.create(bind, checkfirst=True)

    for table in tables:
        op.execute(sa.text(f"UPDATE {table} SET status='committed' WHERE status='completed'"))
        op.execute(sa.text(f"UPDATE {table} SET status='pending' WHERE status='in_progress'"))
        op.alter_column(
            table,
            'status',
            existing_type=old_status,
            type_=new_status,
            existing_nullable=True
        )

    try:
        op.execute(sa.text('DROP TYPE IF EXISTS entry_progress_status'))
        op.execute(sa.text('ALTER TYPE entry_progress_status_new RENAME TO entry_progress_status'))
    except Exception:
        pass


def downgrade():
    bind = op.get_bind()
    tables = [
        'entries_material',
        'entries_equipment',
        'work_order_entries',
        'entries_workers',
        'subcontractor_entries'
    ]

    if bind.dialect.name == 'sqlite':
        for table in tables:
            op.execute(sa.text(f"UPDATE {table} SET status='completed' WHERE status='committed'"))
        return

    old_status.create(bind, checkfirst=True)

    for table in tables:
        op.execute(sa.text(f"UPDATE {table} SET status='completed' WHERE status='committed'"))
        op.alter_column(
            table,
            'status',
            existing_type=new_status,
            type_=old_status,
            existing_nullable=True
        )

    try:
        op.execute(sa.text('DROP TYPE IF EXISTS entry_progress_status_new'))
        op.execute(sa.text('DROP TYPE IF EXISTS entry_progress_status'))
    except Exception:
        pass