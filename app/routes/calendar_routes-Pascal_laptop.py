# app/routes/calendar_routes.py

from flask import (
    Blueprint, render_template, request, session,
    redirect, url_for, jsonify, current_app
)
from app.models import Project

calendar = Blueprint(
    'calendar',
    __name__,
    url_prefix='/calendar'
)

@calendar.route('/', methods=['GET'])
def show_calendar():
    """Display the project+date picker calendar page."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # load all projects (or filter by user_id if you prefer)
    projects = Project.query.all()
    projects_data = [
        {'id': p.id, 'name': p.name, 'number': p.project_number}
        for p in projects
    ]

    return render_template(
        'calendar.html',
        projects=projects_data,
        username=session.get('username', 'Utilisateur')
    )


@calendar.route('/select', methods=['POST'])
def select_calendar_date():
    """
    Handle the form POST from the calendar page.
    Expects form fields 'project_id' and 'report_date'.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    project_val = request.form.get('project_id')
    report_date = request.form.get('report_date')

    if not project_val or not report_date:
        # re-fetch projects to re-render the form with an error
        projects = Project.query.all()
        projects_data = [
            {'id': p.id, 'name': p.name, 'number': p.project_number}
            for p in projects
        ]
        return render_template(
            'calendar.html',
            projects=projects_data,
            username=session.get('username', 'Utilisateur'),
            error="Both project and date are required."
        ), 400

    # stash into session for downstream routes
    session['project_id']  = project_val
    session['report_date'] = report_date
    current_app.logger.info(f"Selected project={project_val}, date={report_date}")

    # jump into your data‐entry dashboard
    return redirect(url_for('data_entry.dashboard'))


@calendar.route('/data', methods=['GET'])
def calendar_data():
    """
    Returns JSON of calendar statuses.
    e.g. which dates have reports in which projects.
    """
    if 'user_id' not in session:
        return jsonify(error="Not authenticated"), 401

    # Build a simple map of project IDs → names
    projects = Project.query.all()
    proj_map = {str(p.id): p.name for p in projects}

    # TODO: replace the mock below with real lookups if desired
    calendar_map = {
        "2025-05-20": {"1": "completed", "2": "in_progress"},
        "2025-05-21": {"2": "not_started"},
    }

    return jsonify(calendar=calendar_map, projects=proj_map), 200
