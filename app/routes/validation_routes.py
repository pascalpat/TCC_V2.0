from flask import Blueprint, request, jsonify, current_app
from app.utils.validation import validate_worker_input

validation_bp = Blueprint('validation', __name__, url_prefix='/validation')

@validation_bp.route('/validate_worker', methods=['POST'])
def validate_worker():
    current_app.logger.debug("validate_worker route hit")
    data = request.get_json()
    worker_name = data.get("worker_name")
    labor_hours = data.get("labor_hours")
    activity_code = data.get("activity_code")

    errors = validate_worker_input(worker_name, labor_hours, activity_code)

    if errors:
        return jsonify({"errors": errors}), 400
    return jsonify({"message": "Validation successful"}), 200
