# app/routes/materials_routes.py

from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.material_models import Material
from app.models.MaterialEntry import MaterialEntry
from app.models.core_models import ActivityCode, Project, PaymentItem
from datetime import datetime

materials_bp = Blueprint('materials_bp', __name__)

# --------------------------------------
# Master Data Routes (Materials catalog)
# --------------------------------------
@materials_bp.route('/list', methods=['GET'])
def get_materials_catalog():
    materials = Material.query.all()
    material_list = [
        {"id": m.id, "name": m.name, "cost_per_unit": m.cost_per_unit, "unit": m.unit}
        for m in materials
    ]
    return jsonify(materials=material_list), 200

# --------------------------------------
# Entry CRUD Routes (Materials tab data)
# --------------------------------------
@materials_bp.route('/confirm-materials', methods=['POST'])
def confirm_materials():
    data = request.get_json() or {}
    usage_lines    = data.get('usage')
    project_number = data.get('project_id')
    date_str       = data.get('date_of_report', data.get('date'))

    if not usage_lines or not project_number or not date_str:
        return jsonify(error="Missing project_id, date_of_report, or usage"), 400

    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify(error="Invalid project number"), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format, expected YYYY-MM-DD"), 400

    created = []
    upserted = []
    for line in usage_lines:
        entity_id   = line.get('entityId')
        manual_name = line.get('manual_name')
        quantity    = line.get('quantity')
        act_id      = line.get('activity_code_id')
        # require either a catalog id OR a manual name, plus quantity & activity
        if (entity_id is None and not manual_name) or quantity is None or act_id is None:
            return jsonify(
                error="Each entry requires entityId (or manual_name), quantity, and activity_code_id"
            ), 400

        # parse & validate quantity
        try:
            qty_val = float(quantity)
        except (TypeError, ValueError):
            return jsonify(error=f"Invalid quantity: {quantity}"), 400

        # lookup activity by PK
        try:
            act_id_int = int(act_id)
        except (TypeError, ValueError):
            return jsonify(error=f"Invalid activity_code_id: {act_id}"), 400
        activity = ActivityCode.query.get(act_id_int)
        if not activity:
            return jsonify(error=f"Activity not found for id: {act_id}"), 400

        # build the entry, only int() the ID if present
        entry = MaterialEntry(
            project_id         = project.id,
            material_id        = int(entity_id) if entity_id else None,
            material_name      = manual_name if not entity_id else None,
            quantity_used      = qty_val,
            activity_code_id   = activity.id,
            date_of_report     = date_obj,
            status             = 'pending',
            created_at         = datetime.utcnow()
        )
        db.session.add(entry)
        created.append(entry)

    db.session.commit()
    return jsonify(records=[e.id for e in created]), 200

@materials_bp.route('/by-project-date', methods=['GET'])
def get_pending_materials():
    project_number = request.args.get('project_id')
    date_str       = request.args.get('date')

    # 1) Validate inputs
    if not project_number or not date_str:
        return jsonify(error="Missing project_id or date"), 400

    project = Project.query.filter_by(project_number=project_number).first()
    if not project:
        return jsonify(error="Invalid project number"), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(error="Invalid date format, expected YYYY-MM-DD"), 400

    # 2) Fetch only “pending” materials for that project & date
    entries = MaterialEntry.query.filter_by(
        project_id      = project.id,
        date_of_report  = date_obj,
        status          = 'pending'
    ).all()

    # 3) Build the JSON result
    materials = []
    for e in entries:
        # Look up payment item if set
        pi = None
        if e.payment_item_id is not None:
            pi = PaymentItem.query.get(e.payment_item_id)

        materials.append({
            "id":                    e.id,
            "material_id":           e.material_id,
            "material_name":         e.material.name if e.material else e.material_name,
            "quantity":              e.quantity_used,
            "activity_id":           e.activity_code_id,
            "activity_code":         e.activity_code.code if e.activity_code else None,
            "activity_description":  e.activity_code.description if e.activity_code else None,
            "payment_item_id":       e.payment_item_id,
            "payment_item_code":     pi.payment_code if pi else None,
            "payment_item_name":     pi.item_name    if pi else None,
            "cwp":                   e.cwp
        })

    return jsonify(materials=materials), 200 

@materials_bp.route('/delete-entry/<int:entry_id>', methods=['DELETE'])
def delete_material_entry(entry_id):
    entry = MaterialEntry.query.get(entry_id)
    if not entry:
        return jsonify(error="Entry not found"), 404
    if entry.status != 'pending':
        return jsonify(error="Only pending entries can be deleted"), 403

    db.session.delete(entry)
    db.session.commit()
    return jsonify(message="Material entry deleted"), 200

@materials_bp.route('/update-entry/<int:entry_id>', methods=['PUT'])
def update_material_entry(entry_id):
    data  = request.get_json() or {}
    qty   = data.get('quantity')
    actid = data.get('activity_code_id')

    if qty is None or actid is None:
        return jsonify(error="Missing quantity or activity_code_id"), 400

    entry = MaterialEntry.query.get(entry_id)
    if not entry:
        return jsonify(error="Entry not found"), 404
    if entry.status != 'pending':
        return jsonify(error="Only pending entries can be updated"), 403

    try:
        entry.quantity_used      = float(qty)
        entry.activity_code_id   = int(actid)
        db.session.commit()
        return jsonify(message="Material entry updated"), 200
    except Exception as e:
        current_app.logger.error(f"Error updating material entry: {e}", exc_info=True)
        db.session.rollback()
        return jsonify(error="Failed to update entry"), 500
