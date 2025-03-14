from flask import Blueprint, request, jsonify, session, current_app
from app.utils.data_loader import load_data
import pandas as pd
from app.models.core_models import Project  # Adjust the import path as necessary
from app import db  # Import the db object


# Define a new blueprint for projects
projects_bp = Blueprint('projects_bp', __name__)

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
        session['project_number'] = project_number
        session.modified = True
        current_app.logger.info(f"Project number saved to session: {project_number}")
        return jsonify({'message': f'Project number {project_number} saved to session'}), 200
    except Exception as e:
        current_app.logger.info(f"Error saving project number: {e}") 
        return jsonify({'error': 'Failed to save project number'}), 500
    
@projects_bp.route('/add', methods=['POST'])
def add_project():
    data = request.json

    # Validate required fields
    required_fields = ['name']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required fields: name'}), 400

    # Validate latitude and longitude
    try:
        Project.validate_coordinates(data.get('latitude'), data.get('longitude'))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Add the project
    project = Project(
        name=data['name'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
        # Add other fields here as needed
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({'message': 'Project added successfully!'}), 201