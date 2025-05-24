import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context
import sqlalchemy as sa

# Set up Alembic logging
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # Flask-SQLAlchemy <3
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Flask-SQLAlchemy >=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')

# Update the SQLAlchemy URL in Alembic
config.set_main_option('sqlalchemy.url', get_engine_url())
# Grab the db instance from Flask-Migrate
target_db = current_app.extensions['migrate'].db


def get_metadata():
    # Get metadata, handling Flask-SQLAlchemy >=3
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def get_filtered_metadata():
    """
    Clone the metadata but omit any phantom 'daily_notes' table.
    """
    metadata = get_metadata()
    new_meta = sa.MetaData()
    for table in metadata.tables.values():
        if table.name != 'daily_notes':
            table.tometadata(new_meta)
    return new_meta


def include_object(obj, name, type_, reflected, compare_to):
    """
    Skip only metadata-only tables named 'daily_notes'.
    """
    if type_ == 'table' and name == 'daily_notes' and not reflected and compare_to is None:
        return False
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=get_filtered_metadata(),
        literal_binds=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get('process_revision_directives') is None:
        conf_args['process_revision_directives'] = process_revision_directives

    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_filtered_metadata(),
            include_object=include_object,
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()

# Select mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
