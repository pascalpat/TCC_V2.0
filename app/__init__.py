# app/__init__.py
import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import DevelopmentConfig  # or ProductionConfig, etc.
from app.utils.data_loader import load_data  # Import the load_data function

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
logger = logging.getLogger(__name__)

# Define the Flask application factory
#def create_app():
#    app = Flask(__name__,template_folder='app/templates')  # Explicitly set the template folder path

    
    # Configuration
#    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tcc.db'
#    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#    app.secret_key = os.urandom(24)  # Replace with a specific secret key for production

    # Initialize extensions
#    db.init_app(app)
#    migrate.init_app(app, db)

    # Blueprints and routes setup (if applicable)
#    from app.models.core_models import Project, ActivityCode
#    from app.models.workforce_models import Worker, WorkerEntry
#    from app.routes.auth_routes import auth_bp  # Adjust the import path as needed
#    app.register_blueprint(auth_bp, url_prefix='/auth')

#    @app.route('/')
#    def home():
#        return render_template('index_old.html')

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
        from .models.daily_models import DailyNoteEntry as DailyNote, DailyPicture, WeatherLog
        from .models.models import TabProgress, Document, SustainabilityMetric
        from .models.purchase_order_models import PurchaseOrder
        from .models.daily_report_status import DailyReportStatus
        from .models.DaylyNoteAttachement import DailyNoteAttachment
        
        print(f"Registered tables: {db.metadata.tables.keys()}")
        
    # call imports for blueprints:
        from .routes import register_blueprints
        register_blueprints(app)
        

    # Define the index route
    @app.route('/')
    def index():
        try:
            # Example function call for project numbers
            #from app.routes.projects_routes import get_project_numbers
            #response = get_project_numbers()
            #project_numbers = response.json.get('project_numbers', [])
            return render_template('index_old.html')
        except Exception as e:
            logger.error(f"Error in index route: {e}")
            return jsonify({'error': str(e)}), 500
        
    @app.route('/load_data', methods=['GET', 'POST'])
    def load_csv_data():
        PROJECT_FILE = 'path/to/your/project_file.csv'  # Define the path to your project file
        EQUIPMENT_FILE = 'path/to/your/equipment_file.csv'  # Define the path to your equipment file
        project_numbers = []
        equipment_list = []

        try:
            projects = load_data(PROJECT_FILE, columns=['project_number'])
            if not projects.empty:
                project_numbers = projects['project_number'].dropna().tolist()
        except Exception as e:
            print(f"Error loading projects: {e}")

        try:
            equipment = load_data(EQUIPMENT_FILE, columns=['equipment_name'])
            equipment_list = equipment.to_dict(orient='records') if not equipment.empty else []
        except Exception as e:
            print(f"Error loading equipment: {e}")

        return render_template('index_old.html', project_numbers=project_numbers, equipment_list=equipment_list)

    # Inject global variables into templates
    @app.context_processor
    def inject_globals():
        return {'username': session.get('username', 'Utilisateur')}

    return app

