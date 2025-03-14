import os
import sys
import logging
from datetime import datetime
import pandas as pd

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

from app import create_app
from app.config import Config
from app.utils.data_loader import load_data

# Ensure additional site-packages are found
sys.path.append(r"C:/Users/patri/AppData/Roaming/Python/Python312/site-packages")

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Ensure DATABASE_URL is set
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///database/TCC.db"
    logger.warning("DATABASE_URL not found in environment, using default: sqlite:///database/TCC.db")

logger.info("Creating Flask app...")
app = create_app()
logger.info("Flask app created.")

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Set secret key for session security
app.secret_key = os.urandom(24)

# Configure Flask session (using filesystem for now)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Define file paths
UPLOAD_FOLDER = 'C:/Users/patri/OneDrive/Bureau/TCC_V2.0/uploads'
EQUIPMENT_FILE = 'C:/Users/patri/OneDrive/Bureau/TCC_V2.0/data/equipment.csv'
PROJECT_FILE = 'C:/Users/patri/OneDrive/Bureau/TCC_V2.0/data/project.csv'

@app.route('/')
def home():
    """Redirect unauthenticated users to login; otherwise, redirect to the calendar page."""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    return redirect(url_for('calendar_bp.calendar_page'))

@app.route('/load_data', methods=['GET', 'POST'])
def load_csv_data():
    """Load CSV data for rendering the index page."""
    project_numbers = []
    equipment_list = []

    try:
        projects = load_data(PROJECT_FILE, columns=['project_number'])
        if not projects.empty:
            project_numbers = projects['project_number'].dropna().tolist()
        else:
            logger.warning("Project file is empty.")
    except Exception as e:
        logger.error(f"Error loading projects: {e}")

    try:
        equipment = load_data(EQUIPMENT_FILE, columns=['equipment_name'])
        equipment_list = equipment.to_dict(orient='records') if not equipment.empty else []
    except Exception as e:
        logger.error(f"Error loading equipment: {e}")

    logger.info(f"Loaded project numbers: {project_numbers}")
    logger.info(f"Loaded equipment list: {equipment_list}")

    return render_template('index_old.html', project_numbers=project_numbers, equipment_list=equipment_list)

# Global variables for tracking progress (for form completion)
completed_tabs = 0
total_tabs = 7

@app.route('/update-progress', methods=['POST'])
def update_progress():
    """Track the progress of form completion."""
    global completed_tabs
    if completed_tabs < total_tabs:
        completed_tabs += 1
    progress_percentage = (completed_tabs / total_tabs) * 100

    data = request.get_json()
    logger.info(f"Received update for tab: {data.get('tab')}")

    return jsonify({'completedTabs': completed_tabs, 'progressPercentage': progress_percentage})

@app.route('/api/get-weather-key', methods=['GET'])
def get_weather_key():
    """Return the weather API key."""
    weather_api_key = os.getenv('WEATHER_API_KEY')
    if not weather_api_key:
        return jsonify({"error": "Weather API key not found."}), 500
    return jsonify({"apiKey": weather_api_key})

@app.route('/api/get-speech-config', methods=['GET'])
def get_speech_config():
    """Return speech recognition API configuration."""
    speech_api_key = os.getenv('SPEECH_API_KEY')
    speech_region = os.getenv('SPEECH_REGION')

    if not speech_api_key or not speech_region:
        return jsonify({"error": "Speech API configuration is missing"}), 500

    return jsonify({"apiKey": speech_api_key, "region": speech_region})

# ---------------------
# Helper Functions
# ---------------------

def collect_daily_pictures(files):
    """
    Collect daily pictures from the provided files.
    
    :param files: dict of uploaded files from the request.
    :return: list of dictionaries containing filename and file content.
    """
    pictures = []
    for file_key in files:
        file = files[file_key]
        if file and file.filename:
            pictures.append({'filename': file.filename, 'content': file.read()})
    return pictures

def collect_work_orders(max_entries, upload_folder):
    """
    Collect work order data from the request.
    
    :param max_entries: Maximum number of work orders expected.
    :param upload_folder: Path where uploaded files should be saved.
    :return: List of work order dictionaries.
    """
    work_orders = []
    for i in range(1, max_entries + 1):
        work_order = {
            'orderNumber': request.form.get(f'workOrder{i}Number', ''),
            'description': request.form.get(f'workOrder{i}Description', ''),
            'hours': request.form.get(f'workOrder{i}Hours', '')
        }
        if any(work_order.values()):
            work_orders.append(work_order)
    return work_orders

def collect_form_data(prefix, fields, max_entries):
    """
    Collect dynamic form data based on a prefix and list of fields.
    
    :param prefix: String prefix used in the form field names.
    :param fields: List of field names.
    :param max_entries: Maximum number of entries expected.
    :return: List of dictionaries with form data.
    """
    form_data = []
    for i in range(1, max_entries + 1):
        entry = {field: request.form.get(f"{prefix}{i}{field}", '') for field in fields}
        if any(entry.values()):
            form_data.append(entry)
    return form_data

def save_data_to_excel(workers_data, work_orders_data, pictures_of_the_day, equipment_data, project_number, general_notes, timestamp):
    """
    Save the collected data to an Excel file.
    
    :param workers_data: Data for workers.
    :param work_orders_data: Data for work orders.
    :param pictures_of_the_day: Data for daily pictures.
    :param equipment_data: Data for equipment.
    :param project_number: The project number identifier.
    :param general_notes: General notes text.
    :param timestamp: Timestamp string for file naming.
    """
    output_file = f'data_{project_number}_{timestamp}.xlsx'
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    pd.DataFrame(workers_data).to_excel(writer, sheet_name='Workers', index=False)
    pd.DataFrame(work_orders_data).to_excel(writer, sheet_name='Work Orders', index=False)
    pd.DataFrame(pictures_of_the_day).to_excel(writer, sheet_name='Daily Pictures', index=False)
    pd.DataFrame(equipment_data).to_excel(writer, sheet_name='Equipment', index=False)
    pd.DataFrame({'Notes': [general_notes]}).to_excel(writer, sheet_name='General Notes', index=False)

    writer.close()
    logger.info(f"Data saved to {output_file}")

# ---------------------
# Main Application Routes
# ---------------------

@app.route('/')
def home():
    """Redirect unauthenticated users to login; otherwise, redirect to the calendar page."""
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    return redirect(url_for('calendar_bp.calendar_page'))

@app.route('/load_data', methods=['GET', 'POST'])
def load_csv_data():
    """Load CSV data for rendering the index page."""
    project_numbers = []
    equipment_list = []

    try:
        projects = load_data(PROJECT_FILE, columns=['project_number'])
        if not projects.empty:
            project_numbers = projects['project_number'].dropna().tolist()
        else:
            logger.warning("Project file is empty.")
    except Exception as e:
        logger.error(f"Error loading projects: {e}")

    try:
        equipment = load_data(EQUIPMENT_FILE, columns=['equipment_name'])
        equipment_list = equipment.to_dict(orient='records') if not equipment.empty else []
    except Exception as e:
        logger.error(f"Error loading equipment: {e}")

    logger.info(f"Loaded project numbers: {project_numbers}")
    logger.info(f"Loaded equipment list: {equipment_list}")

    return render_template('index_old.html', project_numbers=project_numbers, equipment_list=equipment_list)

# Global variables for progress tracking
completed_tabs = 0
total_tabs = 7

@app.route('/update-progress', methods=['POST'])
def update_progress():
    """Track the progress of form completion."""
    global completed_tabs
    if completed_tabs < total_tabs:
        completed_tabs += 1
    progress_percentage = (completed_tabs / total_tabs) * 100

    data = request.get_json()
    logger.info(f"Received update for tab: {data.get('tab')}")

    return jsonify({'completedTabs': completed_tabs, 'progressPercentage': progress_percentage})

@app.route('/api/get-weather-key', methods=['GET'])
def get_weather_key():
    """Return the weather API key."""
    weather_api_key = os.getenv('WEATHER_API_KEY')
    if not weather_api_key:
        return jsonify({"error": "Weather API key not found."}), 500
    return jsonify({"apiKey": weather_api_key})

@app.route('/api/get-speech-config', methods=['GET'])
def get_speech_config():
    """Return speech recognition API configuration."""
    speech_api_key = os.getenv('SPEECH_API_KEY')
    speech_region = os.getenv('SPEECH_REGION')

    if not speech_api_key or not speech_region:
        return jsonify({"error": "Speech API configuration is missing"}), 500

    return jsonify({"apiKey": speech_api_key, "region": speech_region})

# ---------------------
# Run the Flask Application
# ---------------------
if __name__ == '__main__':
    try:
        app_env = os.getenv("FLASK_ENV", "development")
        debug_mode = app_env == "development"

        logger.info(f"Starting Flask app in {app_env} mode")
        logger.info(f"Database URL: {Config.SQLALCHEMY_DATABASE_URI}")

        app.run(host='0.0.0.0', port=5001, debug=debug_mode)
    except Exception as e:
        logger.error(f"Error while starting Flask app: {str(e)}")
