# app/__init__.py
import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Load environment variables early
load_dotenv()

# Use your config map from config.py
from app.config import config_map
from app.utils.data_loader import load_data

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Create and configure the Flask app."""
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )

    # Load configuration from the config_map
    app.config.from_object(config_map.get(config_name, config_map['development']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Register models with app context
    with app.app_context():
        from .models.WorkOrderEntry import WorkOrderEntry
        from .models.work_orders_models import WorkOrder
        from .models.workforce_models import Worker
        from .models.WorkOrderEntryAttachment import WorkOrderEntryAttachment
        from .models.WorkerEntry_models import WorkerEntry
        from .models.SubcontractorEntry import SubcontractorEntry
        from .models.MaterialEntry import MaterialEntry
        from .models.EquipmentEntry_models import EquipmentEntry
        from .models.core_models import ActivityCode, ProjectTask, Project
        from .models.material_models import Material
        from .models.equipment_models import Equipment
        from .models.subcontractor_models import Subcontractor
        from .models.daily_models import DailyNoteEntry as DailyNote, DailyPicture, WeatherLog
        from .models.models import TabProgress, Document, SustainabilityMetric
        from .models.purchase_order_models import PurchaseOrder
        from .models.daily_report_status import DailyReportStatus
        from .models.DailyNoteAttachment import DailyNoteAttachment

        print(f"Registered tables: {db.metadata.tables.keys()}")

        from .routes import register_blueprints
        register_blueprints(app)

    # Routes
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Error in index route: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/load_data', methods=['GET', 'POST'])
    def load_csv_data():
        project_numbers = []
        equipment_list = []

        try:
            projects = load_data(app.config['PROJECT_FILE'], columns=['project_number'])
            if not projects.empty:
                project_numbers = projects['project_number'].dropna().tolist()
        except Exception as e:
            logger.warning(f"Error loading projects: {e}")

        try:
            equipment = load_data(app.config['EQUIPMENT_FILE'], columns=['equipment_name'])
            equipment_list = equipment.to_dict(orient='records') if not equipment.empty else []
        except Exception as e:
            logger.warning(f"Error loading equipment: {e}")

        return render_template('index.html', project_numbers=project_numbers, equipment_list=equipment_list)

    @app.context_processor
    def inject_globals():
        return {'username': session.get('username', 'Utilisateur')}

    return app
