from flask import Blueprint, request, jsonify
from app import db
from app.models.WorkerEntry_models import WorkerEntry
from app.models.EquipmentEntry_models import EquipmentEntry
from app.models.core_models import ActivityCode, Project, PaymentItem
from datetime import datetime

labor_equipment_bp = Blueprint('labor_equipment_bp', __name__, url_prefix='/labor-equipment')

@labor_equipment_bp.route('/confirm-labor-equipment', methods=['POST'])
def confirm_labor_equipment():
    data = request.get_json() or {}
    usage_lines = data.get('usage')
    project_number = data.get('project_id')
    date_str = data.get('date_of_report')

    if not usage_lines or not project_number or not date_str:
        return jsonify(error="Missing project, date, or usage"), 400

    # Resolve project
    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify(error="Invalid project number"), 400

    # Parse date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format"), 400

    upserted = []
    for line in usage_lines:
        # Determine worker vs equipment
        w_id = line.get('employee_id')
        e_id = line.get('equipment_id')
        if w_id is None and e_id is None:
            return jsonify(error="Missing employee_id or equipment_id"), 400

        # Required fields
        hours = line.get('hours')
        act_id = line.get('activity_code_id')
        if hours is None or act_id is None:
            return jsonify(error="Missing hours or activity_code_id"), 400

        # Lookup activity by PK
        try:
            act_id_int = int(act_id)
        except (TypeError, ValueError):
            return jsonify(error=f"Invalid activity ID: {act_id}"), 400
        activity = ActivityCode.query.get(act_id_int)
        if not activity:
            return jsonify(error=f"Invalid activity ID: {act_id}"), 400

        # Optional fields
        pi_id = line.get('payment_item_id')
        cwp_code = line.get('cwp_id')
        is_manual = line.get('is_manual', False)
        manual_name = line.get('manual_name') if is_manual else None

        # Build entry
        if w_id is not None:
            entry = WorkerEntry(
                project_id=project.id,
                worker_id=int(w_id),
                worker_name=manual_name,
                date_of_report=date_obj,
                hours_worked=float(hours),
                activity_id=activity.id,
                payment_item_id=pi_id,
                cwp=cwp_code,
                status='pending'
            )
        else:
            entry = EquipmentEntry(
                project_id=project.id,
                equipment_id=int(e_id),
                equipment_name=manual_name,
                date_of_report=date_obj,
                hours_used=float(hours),
                activity_id=activity.id,
                payment_item_id=pi_id,
                cwp=cwp_code,
                status='pending'
            )

        db.session.add(entry)
        upserted.append(entry)

    # Commit all entries at once
    db.session.commit()
    return jsonify(
        message=f"{len(upserted)} lines saved",
        records=[e.id for e in upserted]
    ), 200

@labor_equipment_bp.route('/by-project-date', methods=['GET'])
def get_pending_labor_equipment():
    project_number = request.args.get('project_id')
    date_str = request.args.get('date')
    if not project_number or not date_str:
        return jsonify(error="Missing project_id or date"), 400

    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify(error="Invalid project number"), 400
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format"), 400

    w_entries = WorkerEntry.query.filter_by(
        project_id=project.id,
        date_of_report=date_obj,
        status="pending"
    ).all()
    e_entries = EquipmentEntry.query.filter_by(
        project_id=project.id,
        date_of_report=date_obj,
        status="pending"
    ).all()

    def serialize(entry, is_worker=True):
        pi = None
        if entry.payment_item_id:
            pi = PaymentItem.query.get(entry.payment_item_id)
        return ({
            "id": entry.id,
            "worker_id": entry.worker_id,
            "worker_name": entry.worker.name if entry.worker else entry.worker_name
        } if is_worker else {
            "id": entry.id,
            "equipment_id": entry.equipment_id,
            "equipment_name": entry.equipment.name if entry.equipment else entry.equipment_name
        }) | {
            "hours": entry.hours_worked if is_worker else entry.hours_used,
            "activity_code": entry.activity.code if entry.activity else None,
            "activity_description": entry.activity.description if entry.activity else None,
            "payment_item_id": entry.payment_item_id,
            "payment_item_code": pi.payment_code if pi else None,
            "payment_item_name": pi.item_name if pi else None,
            "cwp": entry.cwp
        }

    return jsonify(
        workers=[serialize(w, True) for w in w_entries],
        equipment=[serialize(e, False) for e in e_entries]
    ), 200

@labor_equipment_bp.route('/delete-entry/<entry_type>/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_type, entry_id):
    if entry_type == "worker":
        entry = WorkerEntry.query.get(entry_id)
    elif entry_type == "equipment":
        entry = EquipmentEntry.query.get(entry_id)
    else:
        return jsonify(error="Invalid entry type"), 400

    if not entry:
        return jsonify(error="Entry not found"), 404
    if entry.status != 'pending':
        return jsonify(error="Only pending entries can be deleted"), 403

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify(message=f"{entry_type.capitalize()} entry deleted"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

@labor_equipment_bp.route('/update-entry/<entry_type>/<int:entry_id>', methods=['PUT'])
def update_entry(entry_type, entry_id):
    data = request.get_json() or {}
    new_hours = data.get('hours')
    activity_id = data.get('activity_code_id')

    if new_hours is None or activity_id is None:
        return jsonify(error="Missing hours or activity_code_id"), 400

    if entry_type == "worker":
        entry = WorkerEntry.query.get(entry_id)
    elif entry_type == "equipment":
        entry = EquipmentEntry.query.get(entry_id)
    else:
        return jsonify(error="Invalid entry type"), 400

    if not entry:
        return jsonify(error="Entry not found"), 404
    if entry.status != "pending":
        return jsonify(error="Only pending entries can be updated"), 403

    activity = ActivityCode.query.get(int(activity_id))
    if not activity:
        return jsonify(error=f"Invalid activity_id: {activity_id}"), 400

    try:
        if entry_type == "worker":
            entry.hours_worked = float(new_hours)
        else:
            entry.hours_used = float(new_hours)
        entry.activity_id = activity.id
        db.session.commit()
        return jsonify(message=f"{entry_type.capitalize()} entry updated"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
