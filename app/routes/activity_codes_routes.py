from flask import Blueprint, jsonify, current_app
from app.models.core_models import ActivityCode
from app import db

# Define the Blueprint for activity code-related routes
activity_codes_bp = Blueprint('activity_codes', __name__)

# Route to get list of activity codes
@activity_codes_bp.route('/get_activity_codes', methods=['GET'])
def get_activity_codes():
    """
    Fetch all activity codes along with their descriptions from the database
    and return them as JSON.
    """
    try:
        activity_codes = ActivityCode.query.all()
        
        if not activity_codes:
            return jsonify({'status': 'error', 'message': 'No activity codes found'}), 404
        
        # Return both the activity code and description
        activity_codes_list = [{
            "id": ac.id,
            "code": ac.code,
            "description": ac.description
        } for ac in activity_codes]
        
        return jsonify({'status': 'success', 'activity_codes': activity_codes_list})
    
    except Exception as e:
        current_app.logger.error(f"Error fetching activity codes: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
