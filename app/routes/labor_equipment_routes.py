from flask import Blueprint, request, jsonify
from app import db
from app.models.WorkerEntry_models import WorkerEntry
from app.models.EquipmentEntry_models import EquipmentEntry
from app.models.core_models import ActivityCode, Project
from datetime import datetime

labor_equipment_bp = Blueprint('labor_equipment_bp', __name__)


@labor_equipment_bp.route('/confirm-labor-equipment', methods=['POST'])
def confirm_labor_equipment():
    try:
        payload = request.get_json()
        if not payload or 'usage' not in payload:
            return jsonify({"error": "Missing 'usage' array in request"}), 400

        usage_lines = payload['usage']
        if not isinstance(usage_lines, list):
            return jsonify({"error": "Expected 'usage' to be a list"}), 400

        project_number = payload.get("project_id")
        project = Project.query.filter_by(project_number=project_number).first()
        if not project:
            return jsonify({"error": "Invalid project number"}), 400

        project_id = project.id
        date_of_report = payload.get('date_of_report')
        if not date_of_report:
            return jsonify({"error": "Missing date_of_report in request"}), 400

        try:
            date_obj = datetime.strptime(date_of_report, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": f"Invalid date format: {date_of_report}"}), 400

        new_records = []

        for line in usage_lines:
            usage_type = line.get('type')
            entity_id_str = line.get('entityId')
            hours_str = line.get('hours')
            activity_code_str = line.get('activityCode')
            manual_name = line.get('name') or line.get('manual_name')  # Handle both field variants
            is_manual = line.get('isManual', False)

            if not (usage_type and hours_str and activity_code_str):
                return jsonify({"error": "One or more fields missing in usage line"}), 400

            try:
                hours_val = float(hours_str)
            except ValueError:
                return jsonify({"error": f"Invalid hours: {hours_str}"}), 400

            activity = ActivityCode.query.filter_by(code=activity_code_str).first()
            if not activity:
                return jsonify({"error": f"Invalid activity code: {activity_code_str}"}), 400

            activity_id = activity.id

            if usage_type.lower() == 'worker':
                worker_id = int(entity_id_str) if entity_id_str else None
                worker_entry = WorkerEntry(
                    project_id=project_id,
                    worker_id=worker_id,
                    worker_name=manual_name if not worker_id else None,
                    date_of_report=date_obj,
                    hours_worked=hours_val,
                    activity_id=activity_id,
                    status='pending'
                )
                db.session.add(worker_entry)
                new_records.append(worker_entry)

            elif usage_type.lower() == 'equipment':
                equipment_id = int(entity_id_str) if entity_id_str else None
                equipment_entry = EquipmentEntry(
                    project_id=project_id,
                    equipment_id=equipment_id,
                    equipment_name=manual_name if not equipment_id else None,
                    date_of_report=date_obj,
                    hours_used=hours_val,
                    activity_id=activity_id,
                    status='pending'
                )
                db.session.add(equipment_entry)
                new_records.append(equipment_entry)

            else:
                return jsonify({"error": f"Unsupported usage type '{usage_type}'"}), 400

        db.session.commit()

        return jsonify({
            "message": f"{len(new_records)} usage lines saved successfully!",
            "recordsSaved": len(new_records)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@labor_equipment_bp.route('/by-project-date', methods=['GET'])
def get_pending_labor_equipment():
    project_number = request.args.get("project_id")
    date = request.args.get("date")

    if not project_number or not date:
        return jsonify({"error": "Missing project_id or date"}), 400

    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify({"error": "Invalid project number"}), 400

    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    entries_workers = WorkerEntry.query.filter_by(
        project_id=project.id,
        date_of_report=date_obj,
        status="pending"
    ).all()

    entries_equipment = EquipmentEntry.query.filter_by(
        project_id=project.id,
        date_of_report=date_obj,
        status="pending"
    ).all()

    return jsonify({
        "workers": [
            {
                "id": w.id,
                "worker_id": w.worker_id,
                "worker_name": w.worker.name if w.worker else (w.worker_name or f"ID-{w.worker_id}"),
                "hours": w.hours_worked,
                "activity_code": w.activity.code if w.activity else None,
                "activity_description": w.activity.description if w.activity else None
            } for w in entries_workers
        ],
        "equipment": [
            {
                "id": e.id,
                "equipment_id": e.equipment_id,
                "equipment_name": e.equipment.name if e.equipment else (e.equipment_name or f"ID-{e.equipment_id}"),
                "hours": e.hours_used,
                "activity_code": e.activity.code if e.activity else None,
                "activity_description": e.activity.description if e.activity else None
            } for e in entries_equipment
        ]
    }), 200


@labor_equipment_bp.route('/delete-entry/<entry_type>/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_type, entry_id):
    if entry_type == "worker":
        entry = WorkerEntry.query.get(entry_id)
    elif entry_type == "equipment":
        entry = EquipmentEntry.query.get(entry_id)
    else:
        return jsonify({"error": "Invalid entry type"}), 400

    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    if entry.status != 'pending':
        return jsonify({"error": "Only pending entries can be deleted"}), 403

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": f"{entry_type.capitalize()} entry deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@labor_equipment_bp.route('/update-entry/<entry_type>/<int:entry_id>', methods=['PUT'])
def update_entry(entry_type, entry_id):
    data = request.get_json()
    new_hours = data.get("hours")
    activity_code = data.get("activity_code")

    if not new_hours or not activity_code:
        return jsonify({"error": "Missing hours or activity code"}), 400

    if entry_type == "worker":
        entry = WorkerEntry.query.get(entry_id)
    elif entry_type == "equipment":
        entry = EquipmentEntry.query.get(entry_id)
    else:
        return jsonify({"error": "Invalid entry type"}), 400

    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    if entry.status != "pending":
        return jsonify({"error": "Only pending entries can be updated"}), 403

    activity = ActivityCode.query.filter_by(code=activity_code).first()
    if not activity:
        return jsonify({"error": f"Invalid activity code: {activity_code}"}), 400

    try:
        if entry_type == "worker":
            entry.hours_worked = float(new_hours)
        else:
            entry.hours_used = float(new_hours)

        entry.activity_id = activity.id
        db.session.commit()
        return jsonify({"message": f"{entry_type.capitalize()} entry updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
