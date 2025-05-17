# app/routes/labor_equipment_routes.py

from flask import Blueprint, request, jsonify
from app import db
from app.models.WorkerEntry_models import WorkerEntry
from app.models.EquipmentEntry_models import EquipmentEntry
from app.models.core_models import ActivityCode, Project, PaymentItem, CWPackage
from datetime import datetime

labor_equipment_bp = Blueprint('labor_equipment_bp', __name__)

# ----------------------------------------------------------------
# 0) CW-Packages master-data route (for your CWP dropdown JS fetch)
# ----------------------------------------------------------------
@labor_equipment_bp.route('/cw-packages/list', methods=['GET'])
def list_cw_packages():
    all_cwps = CWPackage.query.order_by(CWPackage.code).all()
    return jsonify(cwps=[{"code": c.code, "name": c.name} for c in all_cwps]), 200


# -----------------------------------------------
# 1) Batch-confirm new labour/equipment usage lines
# -----------------------------------------------
@labor_equipment_bp.route('/confirm-labor-equipment', methods=['POST'])
def confirm_labor_equipment():
    data           = request.get_json() or {}
    usage          = data.get('usage')
    project_number = data.get('project_id')
    date_str       = data.get('date_of_report')

    if not usage or not project_number or not date_str:
        return jsonify(error="Missing project, date, or usage"), 400

    proj = Project.query.filter_by(project_number=project_number).first()
    if not proj:
        return jsonify(error="Invalid project number"), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format"), 400

    created_entries = []
    for line in usage:
        w_id        = line.get('employee_id')
        e_id        = line.get('equipment_id')
        is_manual   = line.get('is_manual', False)
        manual_nm   = line.get('manual_name') if is_manual else None
        manual_type = line.get('manual_type') if is_manual else None

        # allow true manual entries even if both IDs are None
        if w_id is None and e_id is None:
            if not (is_manual and manual_nm and manual_type in ('worker','equipment')):
                return jsonify(error="Missing employee_id or equipment_id"), 400

        # required fields
        hours = line.get('hours')
        act_id = line.get('activity_code_id')
        if hours is None or act_id is None:
            return jsonify(error="Missing hours or activity_code_id"), 400

        activity = ActivityCode.query.get(int(act_id))
        if not activity:
            return jsonify(error=f"Invalid activity_code_id: {act_id}"), 400

        pi_id    = line.get('payment_item_id')
        cwp_code = line.get('cwp_id')

        # decide entry type
        if w_id is not None or (is_manual and manual_type=='worker'):
            # Worker entry (manual or by ID)
            entry = WorkerEntry(
                project_id      = proj.id,
                worker_id       = int(w_id) if w_id is not None else None,
                worker_name     = manual_nm if is_manual and manual_type=='worker' else None,
                date_of_report  = date_obj,
                hours_worked    = float(hours),
                activity_id     = activity.id,
                payment_item_id = pi_id,
                cwp             = cwp_code,
                status          = 'pending'
            )

        else:
            # Equipment entry (manual or by ID)
            entry = EquipmentEntry(
                project_id       = proj.id,
                equipment_id     = int(e_id) if e_id is not None else None,
                equipment_name   = manual_nm if is_manual and manual_type=='equipment' else None,
                date_of_report   = date_obj,
                hours_used       = float(hours),
                activity_id      = activity.id,
                payment_item_id  = pi_id,
                cwp              = cwp_code,
                status           = 'pending'
            )

        db.session.add(entry)
        created_entries.append(entry)

    db.session.commit()
    return jsonify(records=[e.id for e in created_entries]), 200

# ------------------------------------------------
# 2) Fetch all the “pending” lines for the UI table
# ------------------------------------------------
@labor_equipment_bp.route('/by-project-date', methods=['GET'])
def get_pending_labor_equipment():
    # 1) Params (front-end should send project_id & report_date)
    project_number = request.args.get('project_id')
    report_date    = request.args.get('report_date') or request.args.get('date')
    if not project_number or not report_date:
        return jsonify(error="Missing project_id or report_date"), 400

    # 2) Lookup Project
    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify(error="Invalid project_id"), 404

    # 3) Parse date
    try:
        date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format, expected YYYY-MM-DD"), 400

    # 4) Fetch pending entries
    w_entries = WorkerEntry.query.filter_by(
        project_id     = project.id,
        date_of_report = date_obj,
        status         = 'pending'
    ).all()

    e_entries = EquipmentEntry.query.filter_by(
        project_id     = project.id,
        date_of_report = date_obj,
        status         = 'pending'
    ).all()

    # 5) Serialization helpers
    def serialize_worker(w):
        pi = w.payment_item  # assuming a relationship exists; else PaymentItem.query.get(w.payment_item_id)
        return {
            "id":                  w.id,
            "type":                "worker",
            "entity_id":           w.worker_id,
            "entity_name":         (w.worker.name if w.worker else w.worker_name),
            "hours":               w.hours_worked,
            "activity_code_id":    w.activity_id,
            "activity_code":       (w.activity.code if w.activity else None),
            "payment_item_id":     w.payment_item_id,
            "payment_item_code":   (pi.payment_code if pi else None),
            "payment_item_name":   (pi.item_name    if pi else None),
            "cwp":                 w.cwp
        }

    def serialize_equipment(e):
        pi = e.payment_item
        return {
            "id":                  e.id,
            "type":                "equipment",
            "entity_id":           e.equipment_id,
            "entity_name":         (e.equipment.name if e.equipment else e.equipment_name),
            "hours":               e.hours_used,
            "activity_code_id":    e.activity_id,
            "activity_code":       (e.activity.code if e.activity else None),
            "payment_item_id":     e.payment_item_id,
            "payment_item_code":   (pi.payment_code if pi else None),
            "payment_item_name":   (pi.item_name    if pi else None),
            "cwp":                 e.cwp
        }

    # 6) Return combined JSON
    return jsonify(
        workers   = [serialize_worker(w) for w in w_entries],
        equipment = [serialize_equipment(e) for e in e_entries]
    ), 200


# ------------------------------------------------
# 3) Delete a single pending entry
# ------------------------------------------------
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


# ------------------------------------------------
# 4) Update (inline-edit) a single pending entry
# ------------------------------------------------
@labor_equipment_bp.route('/update-entry/<entry_type>/<int:entry_id>', methods=['PUT'])
def update_entry(entry_type, entry_id):
    data       = request.get_json() or {}
    new_hours  = data.get('hours')
    activity_id= data.get('activity_code_id')

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
        return jsonify(error=f"Invalid activity_code_id: {activity_id}"), 400

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
