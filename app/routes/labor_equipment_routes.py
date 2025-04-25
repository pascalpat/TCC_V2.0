from flask import Blueprint, request, jsonify
from app import db
from app.models.WorkerEntry_models import WorkerEntry
from app.models.EquipmentEntry_models import EquipmentEntry
from app.models.core_models import ActivityCode, Project, PaymentItem
from datetime import datetime

labor_equipment_bp = Blueprint('labor_equipment_bp', __name__)


@labor_equipment_bp.route('/confirm-labor-equipment', methods=['POST'])
def confirm_labor_equipment():
    try:
        payload = request.get_json()
        if not payload or 'usage' not in payload:
            return jsonify({"error": "Missing 'usage' array in request"}), 400

        usage_lines = payload['usage']
        project_number = payload.get("project_id")
        project = Project.query.filter_by(project_number=project_number).first()
        if not project:
            return jsonify({"error": "Invalid project number"}), 400
        project_id = project.id

        date_str = payload.get('date_of_report')
        if not date_str:
            return jsonify({"error": "Missing date_of_report in request"}), 400
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": f"Invalid date format: {date_str}"}), 400

        new_records = []
        for line in usage_lines:
            usage_type   = line.get('type')
            entity_id    = line.get('entityId')
            hours_str    = line.get('hours')
            activity_str = line.get('activityCode')

            # support both JS and Python keys
            payment_item_id = (
                line.get('payment_item_id')
                or line.get('paymentId')
                or None
            )
            cwp_code = (
                line.get('cwp_code')
                or line.get('cwp')
                or line.get('cwpCode')
                or None
            )
            manual_name = line.get('manual_name') or line.get('name')
            is_manual   = line.get('isManual', False)

            if not (usage_type and hours_str and activity_str):
                return jsonify({"error": "Missing field in usage line"}), 400
            try:
                hours_val = float(hours_str)
            except ValueError:
                return jsonify({"error": f"Invalid hours: {hours_str}"}), 400

            activity = ActivityCode.query.filter_by(code=activity_str).first()
            if not activity:
                return jsonify({"error": f"Invalid activity code: {activity_str}"}), 400
            activity_id = activity.id

            if usage_type.lower() == 'worker':
                w_id = int(entity_id) if entity_id else None
                entry = WorkerEntry(
                    project_id      = project_id,
                    worker_id       = w_id,
                    worker_name     = None if w_id else manual_name,
                    date_of_report  = date_obj,
                    hours_worked    = hours_val,
                    activity_id     = activity_id,
                    payment_item_id = payment_item_id,
                    cwp             = cwp_code,
                    status          = 'pending'
                )
            elif usage_type.lower() == 'equipment':
                e_id = int(entity_id) if entity_id else None
                entry = EquipmentEntry(
                    project_id      = project_id,
                    equipment_id    = e_id,
                    equipment_name  = None if e_id else manual_name,
                    date_of_report  = date_obj,
                    hours_used      = hours_val,
                    activity_id     = activity_id,
                    payment_item_id = payment_item_id,
                    cwp             = cwp_code,
                    status          = 'pending'
                )
            else:
                return jsonify({"error": f"Unsupported type {usage_type}"}), 400

            db.session.add(entry)
            new_records.append(entry)

        db.session.commit()
        return jsonify({
            "message": f"{len(new_records)} lines saved",
            "recordsSaved": len(new_records)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@labor_equipment_bp.route('/by-project-date', methods=['GET'])
def get_pending_labor_equipment():
    project_number = request.args.get("project_id")
    date_str       = request.args.get("date")
    if not project_number or not date_str:
        return jsonify({"error": "Missing project_id or date"}), 400

    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify({"error": "Invalid project number"}), 400
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

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
        # pull PaymentItem relationship if set
        # pi = getattr(entry, 'payment_item', None)
        pi = None
        if entry.payment_item_id:
            pi = PaymentItem.query.get(entry.payment_item_id)

        return {
            "id":                   entry.id,
            **({"worker_id":        entry.worker_id,     "worker_name":    entry.worker.name if entry.worker else entry.worker_name} 
               if is_worker else
               {"equipment_id":     entry.equipment_id,  "equipment_name": entry.equipment.name if entry.equipment else entry.equipment_name}),
            "hours":                entry.hours_worked   if is_worker else entry.hours_used,
            "activity_code":        entry.activity.code if entry.activity else None,
            "activity_description": entry.activity.description if entry.activity else None,
            "payment_item_id":      entry.payment_item_id,
            "payment_item_code":    pi.payment_code   if pi else None,
            "payment_item_name":    pi.item_name      if pi else None,
            "cwp":                  entry.cwp,
        }

    return jsonify({
        "workers":   [serialize(w, True) for w in w_entries],
        "equipment": [serialize(e, False) for e in e_entries]
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
