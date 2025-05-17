# app/__init__.py
import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import DevelopmentConfig  # or ProductionConfig, etc.
from app.utils.data_loader import load_data  # Import the load_data function

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
logger = logging.getLogger(__name__)


def create_app(config_class='app.config.DevelopmentConfig'):
    """Create and configure the Flask app."""
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )
    # Load configurations
    app.config.from_object(config_class)


    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Import all models
    with app.app_context():
        from .models.WorkOrderEntry import WorkOrderEntry
        from .models.work_orders_models import WorkOrder
        from .models.workforce_models import Worker
        from .models.WorkerEntry_models import WorkerEntry
        from .models.WorkOrderEntryAttachment import WorkOrderEntryAttachment
        from .models.SubcontractorEntry import SubcontractorEntry
        from .models.MaterialEntry import MaterialEntry  
        from .models.EquipmentEntry_models import EquipmentEntry
        from .models.core_models import ActivityCode, ProjectTask
        from .models.core_models import Project
        from .models.material_models import Material
        from .models.equipment_models import Equipment
        from .models.subcontractor_models import Subcontractor
        from .models.daily_models import DailyNote, DailyPicture, WeatherLog
        from .models.models import TabProgress, Document, SustainabilityMetric
        from .models.purchase_order_models import PurchaseOrder
        from .models.daily_report_status import DailyReportStatus
        print(f"Registered tables: {db.metadata.tables.keys()}")
        
    # call imports for blueprints:
        from .routes import register_blueprints
        register_blueprints(app)
        
    @app.route('/')
    def root():
        # Send unauthenticated users to login immediately
        return redirect(url_for('auth_bp.login'))
    
    # Inject global variables into templates
    @app.context_processor
    def inject_globals():
        return {'username': session.get('username', 'Utilisateur')}

    return app

