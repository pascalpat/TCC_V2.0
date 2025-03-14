from flask import Blueprint, request, jsonify, current_app, session
from ..models.subcontractor_models import Subcontractor
from .. import db  # Import the database instance

subcontractors_bp = Blueprint('subcontractors_bp', __name__, url_prefix='/subcontractors')

@subcontractors_bp.route('/list', methods=['GET'])
def list_subcontractors():
    """
    Fetch the list of subcontractors from the database based on the active project.
    """
    try:
        project_id = session.get('project_id')  # Ensure project_id is in session
        if not project_id:
            return jsonify({"error": "No active project selected"}), 400

        subcontractors = Subcontractor.query.filter_by(project_id=project_id).all()
        return jsonify({"subcontractors": [sub.to_dict() for sub in subcontractors]}), 200

    except Exception as e:
        current_app.logger.error(f"Error loading subcontractors: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@subcontractors_bp.route('/add', methods=['POST'])
def add_subcontractor():
    """
    Add a new subcontractor entry to the database.
    """
    try:
        project_id = session.get('project_id')  # Ensure project_id is in session
        if not project_id:
            return jsonify({"error": "No active project selected"}), 400

        data = request.json
        required_fields = ["name", "task", "contractType", "totalContractValue", "paymentStatus"]

        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_subcontractor = Subcontractor(
            project_id=project_id,
            name=data["name"],
            task=data["task"],
            contract_type=data["contractType"],
            total_contract_value=float(data["totalContractValue"]),
            payment_status=data["paymentStatus"]
        )
        
        db.session.add(new_subcontractor)
        db.session.commit()

        return jsonify({"message": "Subcontractor added successfully", "data": new_subcontractor.to_dict()}), 201

    except Exception as e:
        current_app.logger.error(f"Error adding subcontractor: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@subcontractors_bp.route('/delete/<int:subcontractor_id>', methods=['DELETE'])
def delete_subcontractor(subcontractor_id):
    """
    Delete a subcontractor entry from the database.
    """
    try:
        subcontractor = Subcontractor.query.get(subcontractor_id)
        if not subcontractor:
            return jsonify({"error": "Subcontractor not found"}), 404

        db.session.delete(subcontractor)
        db.session.commit()

        return jsonify({"message": "Subcontractor deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting subcontractor: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@subcontractors_bp.route('/update/<int:subcontractor_id>', methods=['PUT'])
def update_subcontractor(subcontractor_id):
    """
    Update an existing subcontractor entry in the database.
    """
    try:
        data = request.json
        subcontractor = Subcontractor.query.get(subcontractor_id)
        if not subcontractor:
            return jsonify({"error": "Subcontractor not found"}), 404

        subcontractor.name = data.get("name", subcontractor.name)
        subcontractor.task = data.get("task", subcontractor.task)
        subcontractor.contract_type = data.get("contractType", subcontractor.contract_type)
        subcontractor.total_contract_value = float(data.get("totalContractValue", subcontractor.total_contract_value))
        subcontractor.payment_status = data.get("paymentStatus", subcontractor.payment_status)

        db.session.commit()

        return jsonify({"message": "Subcontractor updated successfully", "data": subcontractor.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating subcontractor: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
