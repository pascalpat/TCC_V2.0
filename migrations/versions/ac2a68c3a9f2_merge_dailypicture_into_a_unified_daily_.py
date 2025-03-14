"""Merge DailyPicture into a unified daily_note_attachments table

Revision ID: ac2a68c3a9f2
Revises: 640d03a9974f
Create Date: 2025-01-02 16:09:44.282251

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac2a68c3a9f2'
down_revision = '640d03a9974f'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Remove 'attachment_url' from daily_notes (if you no longer need it)
    with op.batch_alter_table('daily_notes', schema=None) as batch_op:
        batch_op.drop_column('attachment_url')

    # 2) Create daily_note_attachments (unified attachments)
    op.create_table(
        'daily_note_attachments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('daily_note_id', sa.Integer(), sa.ForeignKey('daily_notes.id'), nullable=False),

        # Fields merged from 'daily_pictures' (plus doc_type)
        sa.Column('file_name',   sa.String(255),   nullable=True),
        sa.Column('file_url',    sa.String(2083),  nullable=False),  # Path/URL to the file
        sa.Column('description', sa.Text(),        nullable=True),   # Description or notes
        sa.Column('doc_type',    sa.String(50),    nullable=True),   # e.g. "jpg", "pdf", "doc"
        sa.Column('taken_at',    sa.DateTime(),    nullable=True),   # Original capture time
        sa.Column('uploaded_at', sa.DateTime(),    nullable=True),   # Time of upload
        sa.Column('coordinates', sa.JSON(),        nullable=True),   # if you keep GPS data
        sa.Column('position',    sa.String(255),   nullable=True),   # e.g. "North Wing"
        sa.Column('size',        sa.Float(),       nullable=True),   # MB or pixel dimension
        sa.Column('tags',        sa.JSON(),        nullable=True),   # array of tags
        sa.Column('captured_by', sa.String(255),   nullable=True),   # user who took the pic
    )

    # 3) Drop daily_pictures (we're moving those fields to daily_note_attachments)
    op.drop_table('daily_pictures')


def downgrade():
    # 1) Recreate the daily_pictures table (if truly reverting)
    op.create_table(
        'daily_pictures',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('daily_log_id', sa.Integer(), sa.ForeignKey('daily_report_data.id'), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_url', sa.String(2083), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('taken_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('activity_code', sa.String(50), sa.ForeignKey('activity_codes.id'), nullable=True),
        sa.Column('work_order_id', sa.Integer(), sa.ForeignKey('work_orders.id'), nullable=True),
        sa.Column('daily_note_id', sa.Integer(), sa.ForeignKey('daily_notes.id'), nullable=True),
        sa.Column('coordinates', sa.JSON(), nullable=True),
        sa.Column('position', sa.String(255), nullable=True),
        sa.Column('size', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('captured_by', sa.String(255), nullable=True),
    )

    # 2) Drop daily_note_attachments
    op.drop_table('daily_note_attachments')

    # 3) Re-add attachment_url to daily_notes if we truly revert
    with op.batch_alter_table('daily_notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attachment_url', sa.String(2083), nullable=True))
