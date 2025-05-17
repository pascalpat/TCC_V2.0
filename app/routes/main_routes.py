# app/routes/main_routes.py
from flask import (
    Blueprint, render_template, current_app,
    redirect, url_for, jsonify, session,
    send_from_directory
)

from flask import (
    Blueprint, render_template, current_app,
    redirect, url_for, jsonify, session,
    send_from_directory
)
import requests
from ..utils.data_loader import save_to_csv

# Blueprint for general app routes and static/template settings
main_bp = Blueprint(
    'main_bp', __name__,
    static_folder='static',
    template_folder='templates'
)

@main_bp.route('/weather')
def weather():
    """
    Proxy endpoint for fetching current weather data from OpenWeatherMap.
    Returns JSON with `temperature` and `icon`, or an error message.
    """
    api_key = current_app.config.get('WEATHER_API_KEY')
    if not api_key:
        # Missing configuration
        return jsonify(error='No API key configured'), 500

    # Hardcoded city for now; could be parameterized later
    city = 'Montreal'
    url = 'https://api.openweathermap.org/data/2.5/weather'
    resp = requests.get(
        url,
        params={'q': city, 'units': 'metric', 'appid': api_key},
        timeout=5
    )

    try:
        data = resp.json()
    except ValueError:
        # API returned non-JSON or malformed
        current_app.logger.error(f"Weather API returned non-JSON: {resp.text}")
        return jsonify(
            temperature=None, icon=None,
            error='Bad response from weather API'
        ), 502

    main_block = data.get('main', {})
    weather_block = data.get('weather') or []

    # Validate payload
    if 'temp' not in main_block or not weather_block or 'icon' not in weather_block[0]:
        current_app.logger.error(f"Unexpected weather payload: {data}")
        return jsonify(
            temperature=None, icon=None,
            error='Incomplete weather data'
        ), 200

    return jsonify(
        temperature=main_block['temp'],
        icon=weather_block[0]['icon']
    ), 200

@main_bp.route('/')
def home():
    """
    Main landing page. Redirects to login if session is not initialized.
    """
    if not all(k in session for k in ('user_id', 'project_id', 'report_date')):
        return redirect(url_for('auth_bp.login'))

    current_app.logger.info("Rendering main page with session data pre-loaded.")
    # Serve the new index.html instead of a stale 'index_old.html'
    return render_template(
        'index.html', 
        user_id=session['user_id'],
        project_id=session['project_id'],
        report_date=session['report_date'],
        username=session.get('username', 'Utilisateur')
    )

@main_bp.route('/favicon.ico')
def favicon():
    """
    Serve the site favicon from the static folder.
    """
    return send_from_directory(
        main_bp.static_folder,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@main_bp.route('/save-report', methods=['POST'])
def save_report():
    """
    Persist daily report data from session into a CSV via utility function.
    Expects `session['daily_data']` and `session['current_reporting_date']` to exist.
    """
    date = session.get('current_reporting_date')
    daily_data = session.get('daily_data', {})

    if not date or date not in daily_data:
        return jsonify({'error': 'No data to save for the selected date'}), 400

    try:
        save_to_csv(daily_data, date)
        return jsonify({'message': f'Data for {date} saved successfully!'}), 200
    except Exception as e:
        current_app.logger.error(f"Error saving data for {date}: {e}")
        return jsonify({'error': 'Failed to save data. Please try again.'}), 500

