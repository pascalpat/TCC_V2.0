"""initial clean migration after ghost FK cleanup

Revision ID: 58d047aa7493
Revises: 
Create Date: 2025-05-19 23:55:03.461987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58d047aa7493'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cw_packages', schema=None) as batch_op:
        batch_op.alter_column('project_id',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=False,
               existing_server_default=sa.text("'DEFAULT_PROJECT'"))
        batch_op.drop_index('ix_cw_packages_project_id')
        batch_op.create_foreign_key('fk_cw_packages_project_id', 'projects', ['project_id'], ['id'])

    with op.batch_alter_table('daily_note_attachments', schema=None) as batch_op:
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.alter_column('uploaded_at', existing_type=sa.DATETIME(), nullable=True, existing_server_default=sa.text('(CURRENT_TIMESTAMP)'))
        batch_op.alter_column('size', existing_type=sa.REAL(), type_=sa.Float(), existing_nullable=True)

    with op.batch_alter_table('daily_pictures', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Enum('pending', 'committed', name='record_status'), nullable=True))
        batch_op.create_foreign_key('fk_daily_pictures_daily_note_id', 'entries_daily_notes', ['daily_note_id'], ['id'])

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Enum('pending', 'committed', name='record_status'), nullable=True))
        batch_op.create_foreign_key('fk_documents_daily_note_id', 'entries_daily_notes', ['daily_note_id'], ['id'])

    with op.batch_alter_table('entries_daily_notes', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_entries_daily_notes_work_order_id', 'work_orders', ['work_order_id'], ['id'])

    with op.batch_alter_table('entries_equipment', schema=None) as batch_op:
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.alter_column('status', existing_type=sa.TEXT(), type_=sa.Enum('pending', 'in_progress', 'completed', name='entry_status'), existing_nullable=True)
        batch_op.alter_column('cwp', existing_type=sa.TEXT(), type_=sa.String(length=50), existing_nullable=True)
        batch_op.alter_column('phase', existing_type=sa.TEXT(), type_=sa.String(length=50), existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_entries_equipment_date_of_report'), ['date_of_report'], unique=False)
        batch_op.create_foreign_key('fk_entries_equipment_payment_item_id', 'payment_items', ['payment_item_id'], ['id'])
        batch_op.create_foreign_key('fk_entries_equipment_project_id', 'projects', ['project_id'], ['id'])
        batch_op.create_foreign_key('fk_entries_equipment_equipment_id', 'equipment', ['equipment_id'], ['id'])
        batch_op.create_foreign_key('fk_entries_equipment_activity_id', 'activity_codes', ['activity_id'], ['id'])

    with op.batch_alter_table('entries_material', schema=None) as batch_op:
        batch_op.alter_column('date_of_report', existing_type=sa.DATE(), nullable=False)
        batch_op.alter_column('cwp', existing_type=sa.TEXT(), type_=sa.String(length=50), existing_nullable=True)
        batch_op.create_foreign_key('fk_entries_material_payment_item_id', 'payment_items', ['payment_item_id'], ['id'])

    with op.batch_alter_table('entries_workers', schema=None) as batch_op:
        batch_op.alter_column('id', existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.alter_column('date_of_report', existing_type=sa.DATE(), nullable=False)
        batch_op.alter_column('project_id', existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column('hours_worked', existing_type=sa.FLOAT(), nullable=False)
        batch_op.alter_column('status', existing_type=sa.TEXT(), type_=sa.Enum('pending', 'in_progress', 'completed', name='entry_status'), existing_nullable=True)
        batch_op.alter_column('cwp', existing_type=sa.TEXT(), type_=sa.String(length=50), existing_nullable=True)
        batch_op.alter_column('phase', existing_type=sa.TEXT(), type_=sa.String(length=50), existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_entries_workers_date_of_report'), ['date_of_report'], unique=False)
        batch_op.create_foreign_key('fk_entries_workers_payment_item_id', 'payment_items', ['payment_item_id'], ['id'])
        batch_op.create_foreign_key('fk_entries_workers_project_id', 'projects', ['project_id'], ['id'])
        batch_op.create_foreign_key('fk_entries_workers_worker_id', 'workers', ['worker_id'], ['id'])
        batch_op.create_foreign_key('fk_entries_workers_activity_id', 'activity_codes', ['activity_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('entries_workers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_entries_workers_date_of_report'))
        batch_op.alter_column('phase',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('cwp',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=sa.Enum('pending', 'in_progress', 'completed', name='entry_status'),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('hours_worked',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('project_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('date_of_report',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('entries_material', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('cwp',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('date_of_report',
               existing_type=sa.DATE(),
               nullable=True)

    with op.batch_alter_table('entries_equipment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_entries_equipment_date_of_report'))
        batch_op.alter_column('phase',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('cwp',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=sa.Enum('pending', 'in_progress', 'completed', name='entry_status'),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('entries_daily_notes', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('status')

    with op.batch_alter_table('daily_pictures', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('status')

    with op.batch_alter_table('daily_note_attachments', schema=None) as batch_op:
        batch_op.alter_column('size',
               existing_type=sa.Float(),
               type_=sa.REAL(),
               existing_nullable=True)
        batch_op.alter_column('uploaded_at',
               existing_type=sa.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('(CURRENT_TIMESTAMP)'))
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)

    with op.batch_alter_table('cw_packages', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_index('ix_cw_packages_project_id', ['project_id'], unique=False)
        batch_op.alter_column('project_id',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False,
               existing_server_default=sa.text("'DEFAULT_PROJECT'"))

    # ### end Alembic commands ###
