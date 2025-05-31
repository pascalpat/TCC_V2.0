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

db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate()

from app.config import config_map, TestingConfig

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
from app.routes.admin_routes               import admin_bp
from app.routes.labor_equipment_routes     import labor_equipment_bp
from app.routes.media_routes               import media_bp
from app.routes.documents_routes           import documents_bp
from app.routes.admin_routes               import admin_bp
from app.utils.auth_decorators import login_required, roles_required



# ─── Application factory ────────────────────────────────────────────────────────
# The application factory pattern is used to create the Flask app instance.
# This allows for better organization and testing of the app.
# The app is configured based on the environment variable FLASK_ENV.
def create_app(config_name: str = None):
    if config_name is None:
        if 'PYTEST_CURRENT_TEST' in os.environ:
            config_name = 'testing'
        else:
            config_name = os.getenv('FLASK_ENV', 'development')

    if isinstance(config_name, type):
        config_class = config_name
    else:
        config_class = config_map.get(config_name, config_map['development'])


    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )

    app.config.from_object(config_class)
    logger.info(f"Starting '{config_name}' mode → DB = {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    if config_class is TestingConfig:
        with app.app_context():
            db.create_all()

    # Apply authentication decorators to blueprints
    protected_bps = [
        calendar_bp,
        data_entry_bp,
        entries_daily_notes_bp,
        main_bp,
        workers_bp,
        equipment_bp,
        activity_codes_bp,
        cwp_bp,
        purchase_orders_bp,
        projects_bp,
        update_progress_bp,
        validation_bp,
        payment_items_bp,
        materials_bp,
        pictures_bp,
        subcontractors_bp,
        work_orders_bp,
        data_persistence_bp,
        labor_equipment_bp,
        media_bp,
        documents_bp,
        admin_bp,
    ]
    for bp in protected_bps:
        if not getattr(bp, "_login_added", False):
            bp.before_request(login_required)
            bp._login_added = True

    if not getattr(admin_bp, "_admin_roles_added", False):
        admin_bp.before_request(roles_required('admin'))
        admin_bp._admin_roles_added = True

    master_bps = [
        workers_bp,
        equipment_bp,
        activity_codes_bp,
        cwp_bp,
        purchase_orders_bp,
        projects_bp,
        payment_items_bp,
        materials_bp,
        subcontractors_bp,
        work_orders_bp,
        documents_bp,
    ]
    for bp in master_bps:
        if not getattr(bp, "_master_roles_added", False):
            bp.before_request(roles_required('admin', 'manager'))
            bp._master_roles_added = True



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
    
    # Context processor to inject global variables into templates
    # This allows you to access session variables in your templates
    # without having to pass them explicitly in every route.
    @app.context_processor  
    def inject_globals():
        return {'username': session.get('username', 'Utilisateur')}

    return app
