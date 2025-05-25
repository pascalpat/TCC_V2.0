# app/routes/main_routes.py
from flask                  import Blueprint, render_template, current_app, redirect, url_for
from app.utils.data_loader  import load_data
import requests
from flask                  import jsonify, session
from ..utils.data_loader    import save_to_csv
import pandas as pd
from flask                  import send_from_directory
from flask                  import current_app


# Create a Blueprint instance for general routes
main_bp = Blueprint('main_bp', __name__, static_folder='static', template_folder='templates')

@main_bp.route('/weather')
def weather():
    api_key = current_app.config.get('WEATHER_API_KEY')
    if not api_key:
        return jsonify(error='No API key configured'), 500

    city = 'Montreal'
    url  = 'https://api.openweathermap.org/data/2.5/weather'
    resp = requests.get(url, params={'q': city, 'units': 'metric', 'appid': api_key})

    try:
        data = resp.json()
    except ValueError:
        current_app.logger.error(f"Weather API returned non-JSON: {resp.text}")
        return jsonify(temperature=None, icon=None, error='Bad response from weather API'), 200

    main_block    = data.get('main', {})
    weather_block = data.get('weather') or []

    # If anything’s missing, log and return nulls
    if 'temp' not in main_block or not weather_block or 'icon' not in weather_block[0]:
        current_app.logger.error(f"Unexpected weather payload: {data}")
        return jsonify(temperature=None, icon=None, error='No temperature data'), 200

    return jsonify(
        temperature=main_block['temp'],
        icon       =weather_block[0]['icon']
    ), 200

@main_bp.route('/')
def home():
    
    """
    Render the main page with pre-filled project and date selection.
    
    """
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))  # Require login first

    project_id  = session.get('project_id')
    report_date = session.get('report_date')

    # Ensure the user has selected a project and date via the calendar
    if not project_id or not report_date:
        return redirect(url_for('calendar_bp.calendar_page'))


    current_app.logger.info("Rendering main page with project and date pre-selected.")
    return render_template('data_entry.html', user_id=session['user_id'], project_id=session['project_id'], report_date=session['report_date'], username=session.get('username', 'Utilisateur'))
    
@main_bp.route('/favicon.ico')
def favicon():
    # Logic for serving the favicon
    return send_from_directory(main_bp.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/save-report', methods=['POST'])
def save_report():
    """
    Save session data for the selected reporting date to the CSV file.
    """
    # Get the current date from session
    date = session.get('report_date') or session.get('current_reporting_date')
    if not date or date not in session.get('daily_data', {}):
        return jsonify({'error': 'No data to save for the selected date'}), 400

    # Save session data to CSV
    try:
        save_to_csv(session['daily_data'], date)
        return jsonify({'message': f'Data for {date} saved successfully!'}), 200
    except Exception as e:
        current_app.logger.debug(f"Error saving data: {e}")
        return jsonify({'error': 'Failed to save data. Please try again.'}), 500
    
