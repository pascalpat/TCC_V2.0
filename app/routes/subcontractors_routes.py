from flask import Blueprint, request, jsonify, current_app, session
from ..models.subcontractor_models import Subcontractor
from ..models.SubcontractorEntry import SubcontractorEntry
from ..models.core_models import ActivityCode, Project
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

@subcontractors_bp.route('/confirm-entries', methods=['POST'])
def confirm_entries():
    """
    Create new SubcontractorEntry rows for the selected project/date.
    Payload: { project_id, date_of_report, usage: [ {...} ] }
    """
    data = request.get_json() or {}
    usage = data.get('usage')
    project_number = data.get('project_id')
    date_str = data.get('date_of_report')
    # validate project_number, date_str, and each usage line...
    # add SubcontractorEntry(status='pending') rows
    created = []
    if usage and project_number and date_str:
        for entry in usage:
            new_entry = SubcontractorEntry(
                project_id=project_number,
                date_of_report=date_str,
                subcontractor_id=entry.get('subcontractor_id'),
                hours=entry.get('hours', 0),
                activity_code=entry.get('activity_code', ''),
                status='pending'
            )
            db.session.add(new_entry)
            created.append(new_entry)
        db.session.commit()
        return jsonify(records=[e.id for e in created]), 200
    else:
        return jsonify({"error": "Missing required fields"}), 400

@subcontractors_bp.route('/by-project-date', methods=['GET'])
def get_pending_entries():
    """Return all pending subcontractor entries for project/date."""
    project_id = request.args.get('project_id')
    date_of_report = request.args.get('date_of_report')
    if not project_id or not date_of_report:
        return jsonify({"error": "Missing required query parameters"}), 400

    entries = SubcontractorEntry.query.filter_by(
        project_id=project_id,
        date_of_report=date_of_report,
        status='pending'
    ).all()
    return jsonify(entries=[e.to_dict() for e in entries]), 200

@subcontractors_bp.route('/delete-entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    # delete pending entry similar to materials_routes.delete_material_entry
    ...

@subcontractors_bp.route('/update-entry/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    # allow inline edit of hours / activity_code etc.
    ...