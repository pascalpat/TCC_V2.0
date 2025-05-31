from flask import Blueprint, request, jsonify, current_app, session
from datetime import datetime
from ..models.subcontractor_models import Subcontractor
from ..models.SubcontractorEntry import SubcontractorEntry
from ..models.core_models import ActivityCode, Project
from .. import db  # Import the database instance

# Routes managing subcontractor data entries

subcontractors_bp = Blueprint('subcontractors_bp', __name__, url_prefix='/subcontractors')

@subcontractors_bp.route('/list', methods=['GET'])
def list_subcontractors():
    """
    Fetch the list of subcontractors from the database based on the active project.
    """
    try:
        project_number = session.get('project_id')  # Stored project number
        if not project_number:
            return jsonify({"error": "No active project selected"}), 400

        proj = Project.query.filter_by(project_number=project_number).first()
        if not proj:
            return jsonify({"error": "Invalid project number"}), 400

        subcontractors = Subcontractor.query.filter_by(project_id=proj.id).all()
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
        project_number = session.get('project_id')  # Stored project number
        if not project_number:   
            return jsonify({"error": "No active project selected"}), 400

        proj = Project.query.filter_by(project_number=project_number).first()
        if not proj:
            return jsonify({"error": "Invalid project number"}), 400
        data = request.json
        required_fields = ["name", "task", "contractType", "totalContractValue", "paymentStatus"]

        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_subcontractor = Subcontractor(
            project_id=proj.id,
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
    Payload: { project_id, date, usage: [ {...} ] }
    """
    data = request.get_json() or {}
    usage = data.get('usage')
    project_number = data.get('project_id')
    date_str = data.get('date')
    # validate project_number, date_str, and each usage line...
    created = []
    if usage and project_number and date_str:
        proj = Project.query.filter_by(project_number=project_number).first()
        if not proj:
            return jsonify({"error": "Invalid project number"}), 400

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
        
        for entry in usage:
            sub_id    = entry.get('subcontractor_id')
            manual_nm = entry.get('manual_name')
            emp       = entry.get('num_employees', 0)
            hours     = entry.get('hours', 0)
            act_id    = entry.get('activity_code_id')

            if sub_id is None and not manual_nm:
                return jsonify(error="Each entry requires subcontractor_id or manual_name"), 400
            if hours is None or act_id is None:
                return jsonify(error="Missing hours or activity_code_id"), 400

            if sub_id is None:
                existing = Subcontractor.query.filter_by(project_id=proj.id, name=manual_nm).first()
                if not existing:
                    existing = Subcontractor(project_id=proj.id, name=manual_nm)
                    db.session.add(existing)
                    db.session.flush()
                sub_id = existing.id

            new_entry = SubcontractorEntry(
                project_id=proj.id,
                date=date_obj,
                subcontractor_id=sub_id,
                num_employees=int(emp or 0),
                labor_hours=float(hours),
                activity_code_id=int(act_id) if act_id else None,
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
    """Return subcontractor entries for project/date, optionally filtered by status."""
    project_number = request.args.get('project_id')
    date_str = request.args.get('date')
    status = request.args.get('status')
    if not project_number or not date_str:
        return jsonify({"error": "Missing required query parameters"}), 400


    proj = Project.query.filter_by(project_number=project_number).first()
    if not proj:
        return jsonify({"error": "Invalid project number"}), 400
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format, expected YYYY-MM-DD"), 400
    
    query = SubcontractorEntry.query.filter_by(
        project_id=proj.id,
        date=date_obj
    )

    if status:
        query = query.filter_by(status=status)
    entries = query.all()
    result = []
    for e in entries:
        result.append({
            "id": e.id,
            "subcontractor_id": e.subcontractor_id,
            "subcontractor_name": e.subcontractor.name if e.subcontractor else None,
            "num_employees": e.num_employees,
            "labor_hours": e.labor_hours,
            "activity_code_id": e.activity_code_id,
            "activity_code": e.activity_code.code if e.activity_code else None,
        })

    return jsonify(entries=result), 200

@subcontractors_bp.route('/delete-entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    # delete pending entry similar to materials_routes.delete_material_entry
    entry = SubcontractorEntry.query.get(entry_id)
    if not entry:
        return jsonify(error="Entry not found"), 404
    if entry.status != 'pending':
        return jsonify(error="Only pending entries can be deleted"), 403

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify(message="Subcontractor entry deleted"), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting subcontractor entry: {e}", exc_info=True)
        db.session.rollback()
        return jsonify(error="Failed to delete entry"), 500

@subcontractors_bp.route('/update-entry/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    # allow inline edit of hours / activity_code etc.
    data = request.get_json() or {}
    hours = data.get('hours')
    activity_id = data.get('activity_code_id')

    if hours is None or activity_id is None:
        return jsonify(error="Missing hours or activity_code_id"), 400

    entry = SubcontractorEntry.query.get(entry_id)
    if not entry:
        return jsonify(error="Entry not found"), 404
    if entry.status != 'pending':
        return jsonify(error="Only pending entries can be updated"), 403

    activity = ActivityCode.query.get(int(activity_id))
    if not activity:
        return jsonify(error=f"Invalid activity_code_id: {activity_id}"), 400

    try:
        entry.labor_hours = float(hours)
        entry.activity_code_id = activity.id
        db.session.commit()
        return jsonify(message="Subcontractor entry updated"), 200
    except Exception as e:
        current_app.logger.error(f"Error updating subcontractor entry: {e}", exc_info=True)
        db.session.rollback()
        return jsonify(error="Failed to update entry"), 500
    
