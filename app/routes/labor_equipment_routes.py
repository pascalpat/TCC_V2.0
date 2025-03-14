# Suppose this goes in a new file: app/routes/labor_equipment_routes.py
# or inside an existing routes file. Adjust imports accordingly.

from flask import Blueprint, request, jsonify, session
from app import db
from app.models.WorkerEntry_models import WorkerEntry  # or wherever your WorkerEntry model is defined
from app.models.EquipmentEntry_models import EquipmentEntry  # or wherever your EquipmentEntry model is
from app.models.core_models import ActivityCode  # if you need to verify code, etc.
import logging


labor_equipment_bp = Blueprint('labor_equipment_bp', __name__)

@labor_equipment_bp.route('/confirm-labor-equipment', methods=['POST'])
def confirm_labor_equipment():
    """
    Accepts JSON usage lines that might be for either a worker or equipment.
    Inserts them into WorkerEntry or EquipmentEntry respectively.

    JSON payload example:
      {
        "usage": [
          {
            "type": "worker",             # or "equipment"
            "entityId": "5",              # worker_id or equipment_id
            "hours": "4.5",
            "activityCode": "ABC123"
          },
          {
            "type": "equipment",
            "entityId": "12",
            "hours": "2.0",
            "activityCode": "XYZ999"
          }
        ]
      }

    Additionally, you might read project_id and date_of_report from session or request if needed.
    """
    try:
        # 1) Parse incoming JSON
        payload = request.get_json()
        if not payload or 'usage' not in payload:
            return jsonify({"error": "Missing 'usage' array in request"}), 400

        usage_lines = payload['usage']
        if not isinstance(usage_lines, list):
            return jsonify({"error": "Expected 'usage' to be a list"}), 400

        # 2) Optionally read project_id, date from session or request
        project_id = session.get('project_id')
        date_of_report = session.get('current_reporting_date')
        if not project_id or not date_of_report:
            return jsonify({"error": "No project ID or date_of_report in session"}), 400

        new_records = []

        # 3) Loop through each usage line
        for line in usage_lines:
            usage_type = line.get('type')  # "worker" or "equipment"
            entity_id_str = line.get('entityId')
            hours_str = line.get('hours')
            activity_code_str = line.get('activityCode')

            # Basic validation
            if not (usage_type and entity_id_str and hours_str and activity_code_str):
                return jsonify({"error": "One or more fields missing in usage line"}), 400

            try:
                entity_id = int(entity_id_str)
                hours_val = float(hours_str)
            except ValueError:
                return jsonify({"error": f"Could not convert entityId={entity_id_str} or hours={hours_str} to numbers."}), 400

            # (Optional) validate the activity code from DB if needed
            # code_obj = ActivityCode.query.filter_by(code=activity_code_str).first()
            # if not code_obj:
            #     return jsonify({"error": f"Invalid activity code: {activity_code_str}"}), 400

            # 4) If usage_type is 'worker', insert into WorkerEntry model
            if usage_type.lower() == 'worker':
                worker_entry = WorkerEntry(
                    project_id=project_id,
                    worker_id=entity_id,
                    date_of_report=date_of_report,
                    hours_worked=hours_val,
                    activity_id=None,  # or code_obj.id if you store a foreign key
                    status='pending'   # adapt as needed
                )
                db.session.add(worker_entry)
                new_records.append(worker_entry)

            # 5) If usage_type is 'equipment', insert into EquipmentEntry model
            elif usage_type.lower() == 'equipment':
                equipment_entry = EquipmentEntry(
                    project_id=project_id,
                    equipment_id=entity_id,
                    date_of_report=date_of_report,
                    hours_used=hours_val,
                    activity_id=None,  # or code_obj.id if you store a foreign key
                    status='pending'   # adapt as needed
                )
                db.session.add(equipment_entry)
                new_records.append(equipment_entry)
            else:
                return jsonify({"error": f"Unsupported usage type '{usage_type}'"}), 400

        # 6) Commit once all lines are processed
        db.session.commit()

        return jsonify({
            "message": f"{len(new_records)} usage lines saved successfully!",
            "recordsSaved": len(new_records)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
