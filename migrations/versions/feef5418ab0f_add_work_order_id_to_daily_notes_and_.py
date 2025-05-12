"""b/migrations/versions/feef5418ab0f_add_work_order_id_to_daily_notes_and_.py

Revision ID: feef5418ab0f
Revises: a422288fac32
Create Date: 2025-05-11 09:48:16.981471
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'feef5418ab0f'
down_revision = 'a422288fac32'
branch_labels = None
depends_on = None


def upgrade():
    # -------------------------------------------------
    # Clean up leftover temp tables
    # -------------------------------------------------
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_daily_notes")
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_daily_pictures")

    # -------------------------------------------------
    # DAILY_NOTES: back-fill existing `content` column
    # -------------------------------------------------
    # (we do NOT add `content` here, it's already present)
    op.execute("UPDATE daily_notes SET content = note")

    # -------------------------------------------------
    # DAILY_NOTES: add work_order_id + FK
    # -------------------------------------------------
    with op.batch_alter_table('daily_notes', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('work_order_id', sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            'fk_daily_notes_work_order_id',
            'work_orders',
            ['work_order_id'],
            ['id']
        )

    # -------------------------------------------------
    # DAILY_PICTURES: back-fill & enforce NOT NULL
    # -------------------------------------------------
    op.execute(
        "UPDATE daily_pictures "
        "SET uploaded_at = CURRENT_TIMESTAMP "
        "WHERE uploaded_at IS NULL"
    )
    with op.batch_alter_table('daily_pictures', schema=None) as batch_op:
        batch_op.alter_column(
            'uploaded_at',
            existing_type=sa.DATETIME(),
            nullable=False
        )
        batch_op.alter_column(
            'activity_code',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.Integer(),
            existing_nullable=True
        )

    # -------------------------------------------------
    # ENTRIES_EQUIPMENT (unchanged)
    # -------------------------------------------------
    with op.batch_alter_table('entries_equipment', schema=None) as batch_op:
        batch_op.alter_column('id',
            existing_type=sa.INTEGER(), nullable=False, autoincrement=True)
        batch_op.alter_column('status',
            existing_type=sa.TEXT(),
            type_=sa.Enum('pending','in_progress','completed',
                          name='entry_status'),
            existing_nullable=True)
        batch_op.alter_column('cwp',
            existing_type=sa.TEXT(),
            type_=sa.String(length=50),
            existing_nullable=True)
        batch_op.alter_column('phase',
            existing_type=sa.TEXT(),
            type_=sa.String(length=50),
            existing_nullable=True)
        batch_op.create_index(
            batch_op.f('ix_entries_equipment_date_of_report'),
            ['date_of_report'], unique=False)
        batch_op.create_foreign_key('fk_eqp_equipment_id', 'equipment',
            ['equipment_id'], ['id'])
        batch_op.create_foreign_key('fk_eqp_payment_item_id', 'payment_items',
            ['payment_item_id'], ['id'])
        batch_op.create_foreign_key( 'fk_eqp_activity_id', 'activity_codes',
            ['activity_id'], ['id'])
        batch_op.create_foreign_key('fk_eqp_project_id', 'projects',
            ['project_id'], ['id'])

    # -------------------------------------------------
    # ENTRIES_MATERIAL (unchanged)
    # -------------------------------------------------
    with op.batch_alter_table('entries_material', schema=None) as batch_op:
        batch_op.alter_column('date_of_report',
            existing_type=sa.DATE(), nullable=False)
        batch_op.alter_column('cwp',
            existing_type=sa.TEXT(),
            type_=sa.String(length=50),
            existing_nullable=True)
        batch_op.create_foreign_key('fk_mat_payment_item_id', 'payment_items',
            ['payment_item_id'], ['id'])

    # -------------------------------------------------
    # ENTRIES_WORKERS (unchanged)
    # -------------------------------------------------
    with op.batch_alter_table('entries_workers', schema=None) as batch_op:
        batch_op.alter_column('id',
            existing_type=sa.INTEGER(),
            nullable=False,
            autoincrement=True)
        batch_op.alter_column('date_of_report',
            existing_type=sa.DATE(), nullable=False)
        batch_op.alter_column('project_id',
            existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column('hours_worked',
            existing_type=sa.FLOAT(), nullable=False)
        batch_op.alter_column('status',
            existing_type=sa.TEXT(),
            type_=sa.Enum('pending','in_progress','completed',
                          name='entry_status'),
            existing_nullable=True)
        batch_op.alter_column('cwp',
            existing_type=sa.TEXT(),
            type_=sa.String(length=50),
            existing_nullable=True)
        batch_op.alter_column('phase',
            existing_type=sa.TEXT(),
            type_=sa.String(length=50),
            existing_nullable=True)
        batch_op.create_index(
            batch_op.f('ix_entries_workers_date_of_report'),
            ['date_of_report'], unique=False)
        batch_op.create_foreign_key('fk_wrk_worker_id', 'workers',
            ['worker_id'], ['id'])
        batch_op.create_foreign_key('fk_wrk_payment_item_id', 'payment_items',
            ['payment_item_id'], ['id'])
        batch_op.create_foreign_key('fk_wrk_activity_id', 'activity_codes',
            ['activity_id'], ['id'])
        batch_op.create_foreign_key( 'fk_wrk_project_id', 'projects',
            ['project_id'], ['id'])

    # -------------------------------------------------
    # WEATHER_LOGS (unchanged)
    # -------------------------------------------------
    with op.batch_alter_table('weather_logs', schema=None) as batch_op:
        batch_op.alter_column('severity',
            existing_type=sa.VARCHAR(length=6), nullable=False)
        batch_op.alter_column('work_impact',
            existing_type=sa.VARCHAR(length=13), nullable=False)


def downgrade():
    # WEATHER_LOGS revert
    with op.batch_alter_table('weather_logs', schema=None) as batch_op:
        batch_op.alter_column('work_impact',
            existing_type=sa.VARCHAR(length=13), nullable=True)
        batch_op.alter_column('severity',
            existing_type=sa.VARCHAR(length=6), nullable=True)

    # ENTRIES_WORKERS revert
    with op.batch_alter_table('entries_workers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_entries_workers_date_of_report'))
        batch_op.alter_column('phase',
            existing_type=sa.String(length=50), type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('cwp',
            existing_type=sa.String(length=50), type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('status',
            existing_type=sa.Enum('pending','in_progress','completed',
                                  name='entry_status'),
            type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('hours_worked',
            existing_type=sa.FLOAT(), nullable=True)
        batch_op.alter_column('project_id',
            existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column('date_of_report',
            existing_type=sa.DATE(), nullable=True)
        batch_op.alter_column('id',
            existing_type=sa.INTEGER(), nullable=True, autoincrement=True)

    # ENTRIES_MATERIAL revert
    with op.batch_alter_table('entries_material', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('cwp',
            existing_type=sa.String(length=50), type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('date_of_report',
            existing_type=sa.DATE(), nullable=True)

    # ENTRIES_EQUIPMENT revert
    with op.batch_alter_table('entries_equipment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_entries_equipment_date_of_report'))
        batch_op.alter_column('phase',
            existing_type=sa.String(length=50), type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('cwp',
            existing_type=sa.String(length=50), type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('status',
            existing_type=sa.Enum('pending','in_progress','completed',
                                  name='entry_status'),
            type_=sa.TEXT(),
            existing_nullable=True)
        batch_op.alter_column('id',
            existing_type=sa.INTEGER(), nullable=True, autoincrement=True)

    # DAILY_PICTURES revert
    with op.batch_alter_table('daily_pictures', schema=None) as batch_op:
        batch_op.alter_column('activity_code',
            existing_type=sa.Integer(), type_=sa.VARCHAR(length=50),
            existing_nullable=True)
        batch_op.alter_column('uploaded_at',
            existing_type=sa.DATETIME(), nullable=True)

    # DAILY_NOTES revert (drop our FK & work_order_id)
    with op.batch_alter_table('daily_notes', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_daily_notes_work_order_id', type_='foreignkey')
        batch_op.drop_column('work_order_id')
