"""rename entry_status enums

Revision ID: f431effa4856
Revises: 3c0e1c3ef3a9
Create Date: 2025-05-29 00:31:00.815598
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f431effa4856'
down_revision = '3c0e1c3ef3a9'
branch_labels = None
depends_on = None

entry_progress_status = sa.Enum('pending', 'in_progress', 'completed', name='entry_progress_status')
old_progress_status = sa.Enum('pending', 'in_progress', 'completed', name='entry_status')


daily_note_status = sa.Enum('pending', 'committed', 'rejected', name='daily_note_status')
old_daily_status = sa.Enum('pending', 'committed', 'rejected', name='entry_status')


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # SQLite stores enums as TEXT; no type changes needed
        return

    # Create new enum types (if needed)
    entry_progress_status.create(bind, checkfirst=True)
    daily_note_status.create(bind, checkfirst=True)

    tables = [
        'entries_material',
        'entries_equipment',
        'work_order_entries',
        'entries_workers',
        'subcontractor_entries'
    ]
    for table in tables:
        op.alter_column(
            table,
            'status',
            existing_type=old_progress_status,
            type_=entry_progress_status,
            existing_nullable=True
        )

    op.alter_column(
        'entries_daily_notes',
        'status',
        existing_type=old_daily_status,
        type_=daily_note_status,
        existing_nullable=True
    )

    # Drop old enum type if no longer used (PostgreSQL specific)
    try:
        op.execute(sa.text('DROP TYPE IF EXISTS entry_status'))
    except Exception:
        pass


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        return

    old_progress_status.create(bind, checkfirst=True)
    old_daily_status.create(bind, checkfirst=True)

    tables = [
        'entries_material',
        'entries_equipment',
        'work_order_entries',
        'entries_workers',
        'subcontractor_entries'
    ]
    for table in tables:
        op.alter_column(
            table,
            'status',
            existing_type=entry_progress_status,
            type_=old_progress_status,
            existing_nullable=True
        )

    op.alter_column(
        'entries_daily_notes',
        'status',
        existing_type=daily_note_status,
        type_=old_daily_status,
        existing_nullable=True
    )

    try:
        op.execute(sa.text('DROP TYPE IF EXISTS entry_progress_status'))
        op.execute(sa.text('DROP TYPE IF EXISTS daily_note_status'))
    except Exception:
        pass