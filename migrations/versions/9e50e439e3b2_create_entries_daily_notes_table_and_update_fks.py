"""create entries_daily_notes table and update FK references

Revision ID: 9e50e439e3b2
Revises: e8d383e099b7
Create Date: 2025-05-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9e50e439e3b2'
down_revision = 'e8d383e099b7'
branch_labels = None
depends_on = None


def upgrade():
    # Create entries_daily_notes table
    op.create_table(
        'entries_daily_notes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('note_datetime', sa.DateTime(), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', name='note_priority_enum'), server_default='low'),
        sa.Column('activity_code_id', sa.Integer(), sa.ForeignKey('activity_codes.id'), nullable=True),
        sa.Column('editable_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_entries_daily_notes_note_datetime'), 'entries_daily_notes', ['note_datetime'], unique=False)

    # Drop old daily_notes table if it exists
    op.execute('DROP TABLE IF EXISTS daily_notes')


def downgrade():
    # Recreate old daily_notes table
    op.create_table(
        'daily_notes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('daily_log_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', name='note_priority_enum'), nullable=True),
        sa.Column('linked_activity_code', sa.Integer(), nullable=True),
        sa.Column('attachment_url', sa.String(length=2083), nullable=True),
        sa.Column('editable_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['daily_log_id'], ['daily_report_data.id']),
        sa.ForeignKeyConstraint(['linked_activity_code'], ['activity_codes.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
    )

    op.drop_index(op.f('ix_entries_daily_notes_note_datetime'), table_name='entries_daily_notes')
    op.drop_table('entries_daily_notes')
