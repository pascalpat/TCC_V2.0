from flask import Blueprint, request, jsonify, session, current_app, render_template
from app.utils.data_loader import load_data
import pandas as pd
from app.models.core_models import Project  # Adjust the import path as necessary
from app import db  # Import the db object
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

# Define a new blueprint for projects
projects_bp = Blueprint('projects_bp', __name__, url_prefix='/projects')

# Route to get list of project numbers
@projects_bp.route('/list', methods=['GET'])
def get_project_numbers():
    try:
        #project_file = current_app.config.get("PROJECT_FILE", "fallback_project.csv")
        projects = Project.query.all()
        project_numbers = [{'id': project.id, 'name': project.name, 'project_number': project.project_number, 'status': project.status} for project in projects]
        return jsonify({'project_numbers': project_numbers}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error loading project numbers: {e}")
        return jsonify({'error': str(e)}), 500


# Save selected project to session
@projects_bp.route('/set_project', methods=['POST'])
def set_project():
    try:
        project_number = request.json.get('projectNumber')
        if not project_number:
            return jsonify({'error': 'No project number provided'}), 400
        
        project = Project.query.filter_by(project_number=project_number).first()
        if not project:
            return jsonify({'error': 'Invalid project number'}), 404

        # Save project number to session
        session['project_id'] = project_number
        session['project_number'] = project_number  # legacy key
        session.modified = True
        current_app.logger.info(f"Project number saved to session: {project_number}")
        return jsonify({'message': f'Project number {project_number} saved to session'}), 200
    except Exception as e:
        current_app.logger.info(f"Error saving project number: {e}") 
        return jsonify({'error': 'Failed to save project number'}), 500
    
@projects_bp.route('/add', methods=['POST'])
def add_project():
    data = request.json or {}
    required = ['name', 'project_number', 'category']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

    # Check for duplicate project by number or name before creating
    existing = Project.query.filter_by(project_number=data['project_number']).first()
    if existing:
        return jsonify({'error': f"Project number '{data['project_number']}' already exists"}), 400

    def parse_float(value):
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid numeric value")

    def parse_int(value):
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid integer value")

    def parse_bool(value):
        if value in (None, ""):
            return None
        if isinstance(value, bool):
            return value
        str_val = str(value).strip().lower()
        if str_val in {"true", "1", "yes"}:
            return True
        if str_val in {"false", "0", "no"}:
            return False
        raise ValueError("Invalid boolean value")

    try:
        latitude = parse_float(data.get('latitude'))
        longitude = parse_float(data.get('longitude'))
        Project.validate_coordinates(latitude, longitude)

        budget = parse_float(data.get('budget'))
        original_budget = parse_float(data.get('original_budget'))
        revised_budget = parse_float(data.get('revised_budget'))
        contingency_fund = parse_float(data.get('contingency_fund'))

        integration_status = parse_bool(data.get('integration_status')) if data.get('integration_status') not in (None, '') else False

        local_hires = parse_int(data.get('local_hires'))
        previous_project_id = parse_int(data.get('previous_project_id'))
        benchmark_cost_per_unit = parse_float(data.get('benchmark_cost_per_unit'))
        critical_path_duration = parse_int(data.get('critical_path_duration'))
        safety_incidents = parse_int(data.get('safety_incidents'))




    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    def parse_date(val):
        return datetime.strptime(val, '%Y-%m-%d').date() if val else None

    project = Project(
        name=data['name'],
        description=data.get('description'),
        project_number=data['project_number'],
        category=data['category'],
        status=data.get('status', 'planned'),
        client_name=data.get('client_name'),
        project_manager=data.get('project_manager'),
        address=data.get('address'),
        budget=budget,
        original_budget=original_budget,
        revised_budget=revised_budget,
        contingency_fund=contingency_fund,
        risk_level=data.get('risk_level'),
        risk_notes=data.get('risk_notes'),
        map_url=data.get('map_url'),
        latitude=latitude,
        longitude=longitude,
        picture_url=data.get('picture_url'),
        video_capture_url=data.get('video_capture_url'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        notes=data.get('notes'),
        plan_repository_url=data.get('plan_repository_url'),
        sustainability_rating=data.get('sustainability_rating'),
        sustainability_goals=data.get('sustainability_goals'),
        collaboration_url=data.get('collaboration_url'),
        integration_status=integration_status,
        audit_due_date=parse_date(data.get('audit_due_date')),
        compliance_status=data.get('compliance_status'),
        local_hires=local_hires,
        community_engagement_notes=data.get('community_engagement_notes'),
        previous_project_id=previous_project_id,
        benchmark_cost_per_unit=benchmark_cost_per_unit,
        tags=data.get('tags'),
        critical_path_duration=critical_path_duration,
        key_milestones=data.get('key_milestones'),
        safety_incidents=safety_incidents,
        incident_notes=data.get('incident_notes'),
        bim_file_url=data.get('bim_file_url'),
        bim_model_id=data.get('bim_model_id'),
        updated_by=data.get('updated_by')
    )
    db.session.add(project)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Project number or name already exists'}), 400

    return jsonify({'message': 'Project added successfully', 'id': project.id}), 201

@projects_bp.route("/entry", methods=["GET"])
def project_entry_form():
    """Display the project entry form."""
    return render_template("projects_entry.html")