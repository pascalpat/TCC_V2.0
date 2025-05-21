# app/routes/calendar_routes.py

from flask import (
    Blueprint, jsonify, session, render_template, 
    redirect, url_for, request
)
# Remove unused imports like PROJECT_FILE and load_data if you're no longer using CSV.
# from ..utils.data_loader import load_data
# from ..config import PROJECT_FILE

from ..utils.user_id_by_projects import get_user_projects  # If you're still using this helper
from ..models.core_models import Project  # Import the Project model
from .. import db
import logging

calendar_bp = Blueprint('calendar_bp', __name__)

@calendar_bp.route('/', methods=['GET', 'POST'])
def calendar_page():
    """
    Render the calendar HTML page and handle project/date selection.
    """
    # Ensure user is authenticated
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        report_date = request.form.get('report_date')

        if not project_id or not report_date:
            return render_template('calendar.html', error="Both project and date are required.")

        # Save project_id and report_date in session
        session['project_id'] = project_id
        session['report_date'] = report_date
        return redirect(url_for('main_bp.home'))  # e.g., loads index.html

    # Query projects directly from the database
    user_projects = Project.query.all()
    projects_data = [
        {'id': project.id, 'name': project.name, 'number': project.project_number}
        for project in user_projects
    ]
    
    # Render the calendar page, passing project list and optional username
    return render_template(
        'calendar.html', 
        projects=projects_data, 
        username=session.get('username', 'Utilisateur')
    )

@calendar_bp.route('/calendar-data', methods=['GET'])
def get_calendar_data():
    """
    Fetch calendar data with fallback for missing session data.
    Returns a mock structure for demonstration purposes.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        # Optionally fetch user-specific projects, or just get all projects
        # user_projects = get_user_projects(session['user_id'])
        projects = Project.query.all()
        
        project_data = {
            str(project.id): project.name 
            for project in projects
        }

        # Mock calendar data; replace with real logic if needed
        calendar_data = {
            "2024-12-10": {"24-401": "completed", "24-404": "in_progress"},
            "2024-12-11": {"24-401": "not_started"},
            "2024-12-13": {"24-401": "completed", "24-404": "completed"},
        }

        return jsonify({'calendar': calendar_data, 'projects': project_data}), 200

    except Exception as e:
        logging.error(f"Error in get_calendar_data: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
