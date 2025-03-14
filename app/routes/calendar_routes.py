# app/routes/calendar_routes.py

from flask import (Blueprint, jsonify, session, render_template, redirect, url_for, request) 
# Remove unused imports like PROJECT_FILE and load_data if you're no longer using CSV.
# from ..utils.data_loader import load_data
# from ..config import PROJECT_FILE

from ..utils.user_id_by_projects import get_user_projects  # If you're still using this helper
from ..models.core_models import Project  # Import the Project model
from ..models.daily_report_status import DailyReportStatus  # your DailyReportStatus model
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

        # Redirect to wherever you handle data entry or landing
        return redirect(url_for('main_bp.home'))  # or your chosen route

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
    Return real calendar data from daily_report_statuses.
    The resulting JSON structure looks like:
      {
        "calendar": {
          "2025-01-06": { "24-401": "completed" },
          "2025-01-07": { "24-401": "in_progress", "24-404": "completed" }
        },
        "projects": {
          "1": "24-401 - My First Project",
          "2": "24-404 - Another Project"
        }
      }
    """
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        # 1) Get all Projects for labeling or a user-specific subset if needed
        projects = Project.query.all()

        # Build a map: project_id -> "project_number" or "24-401 - MyProject"
        project_map = {
            p.id: f"{p.project_number}"  # or add more detail if you'd like
            for p in projects
        }

        # 2) Query daily_report_status table
        status_rows = DailyReportStatus.query.all()  

        # 3) Build the calendar dictionary
        #    date_str => { "project_number": "status", ... }
        calendar_data = {}

        for row in status_rows:
            date_str = row.report_date.isoformat()  # e.g. "2025-01-06"
            project_label = project_map.get(row.project_id, f"proj_{row.project_id}")

            # We can use the row.report_status directly:
            status_str = row.report_status
            # If you want to combine tab statuses into a single daily status, 
            # apply that logic here. For example:
            #
            #   tab_list = [
            #     row.workers_tab, row.materials_tab, row.equipment_tab,
            #     row.notes_tab, row.pictures_tab, row.subcontractors_tab, row.workorders_tab
            #   ]
            #   if all(t == 'completed' for t in tab_list):
            #       status_str = 'completed'
            #   elif any(t == 'in_progress' for t in tab_list):
            #       status_str = 'in_progress'
            #   else:
            #       status_str = 'pending'

            if date_str not in calendar_data:
                calendar_data[date_str] = {}
            
            calendar_data[date_str][project_label] = status_str

        # 4) Also build a simpler “projects” dictionary for the front-end
        project_data = {
            str(p.id): f"{p.project_number} - {p.name}"
            for p in projects
        }

        return jsonify({
            'calendar': calendar_data,
            'projects': project_data
        }), 200
    
    except Exception as e:
        logging.error(f"Error in get_calendar_data: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500