# app/__init__.py

import os
import logging
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

db = SQLAlchemy()
migrate = Migrate()

from app.config import config_map

# Blueprint imports
from app.routes.auth_routes                import auth_bp
from app.routes.calendar_routes            import calendar_bp
from app.routes.data_entry_routes          import data_entry_bp
from app.routes.entries_daily_notes_routes import entries_daily_notes_bp
from app.routes.main_routes                import main_bp
from app.routes.workers_routes             import workers_bp
from app.routes.equipment_routes           import equipment_bp
from app.routes.activity_codes_routes      import activity_codes_bp
from app.routes.cwp_routes                 import cwp_bp
from app.routes.purchase_orders_routes     import purchase_orders_bp
from app.routes.projects_routes            import projects_bp
from app.routes.update_progress_routes     import update_progress_bp
from app.routes.validation_routes          import validation_bp
from app.routes.payment_items_routes       import payment_items_bp
from app.routes.materials_routes           import materials_bp
from app.routes.pictures_routes            import pictures_bp
from app.routes.subcontractors_routes      import subcontractors_bp
from app.routes.work_orders_routes         import work_orders_bp
from app.routes.data_persistence           import data_persistence_bp
from app.routes.labor_equipment_routes     import labor_equipment_bp
from app.routes.media_routes               import media_bp
from app.routes.documents_routes           import documents_bp
from app.routes.admin_routes               import admin_bp

def create_app(config_name: str = None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )

    app.config.from_object(config_map.get(config_name, config_map['development']))
    logger.info(f"Starting '{config_name}' mode → DB = {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(data_entry_bp)
    app.register_blueprint(entries_daily_notes_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(workers_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(activity_codes_bp)
    app.register_blueprint(cwp_bp)
    app.register_blueprint(purchase_orders_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(update_progress_bp)
    app.register_blueprint(validation_bp)
    app.register_blueprint(payment_items_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(pictures_bp)
    app.register_blueprint(subcontractors_bp)
    app.register_blueprint(work_orders_bp)
    app.register_blueprint(data_persistence_bp)
    app.register_blueprint(labor_equipment_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)

    # Redirect the root URL to your data-entry page instead of the old HTML
    @app.route('/')
    def root():
        """Redirect to the main data-entry page."""
        return redirect(url_for('data_entry_bp.submit_data_entry'))

    @app.context_processor
    def inject_globals():
        return {'username': session.get('username', 'Utilisateur')}

    return app
