# app/routes/equipment_routes.py

from flask import Blueprint, session, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.equipment_models import Equipment  # Ensure this import is correct

# Define the Blueprint for equipment-related routes
equipment_bp = Blueprint('equipment_bp', __name__, url_prefix='/equipment')

@equipment_bp.route('/list', methods=['GET'])
def get_equipment_list():
    """Fetch the list of available equipment from the database with better error handling."""
    try:
        equipment = Equipment.query.all()
        current_app.logger.info(f"Fetched {len(equipment)} equipment items from database.")

        # ✅ Check if the database has no equipment records
        if not equipment:
            return jsonify({'message': "No equipment found in the database.", 'equipment': []}), 200

        # ✅ Filter out invalid rows (skip NULL names or statuses)
        equipment_list = [
            {
                'id': equip.id,
                'name': equip.name if equip.name else "Unnamed Equipment",
                'serial_number': equip.serial_number if equip.serial_number else "Unknown Serial",
                'maintenance_status': equip.maintenance_status if equip.maintenance_status in ['operational', 'under_maintenance', 'out_of_service'] else "operational"
            }
            for equip in equipment if equip.name and equip.maintenance_status
        ]

        # ✅ If all records were invalid, return an empty response with a warning message
        if not equipment_list:
            return jsonify({'message': "All equipment records are invalid or missing required fields.", 'equipment': []}), 200

        return jsonify({'equipment': equipment_list}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error fetching equipment: {str(e)}", exc_info=True)
        return jsonify({'error': "Database error while fetching equipment. Please try again later."}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error fetching equipment: {str(e)}", exc_info=True)
        return jsonify({'error': "An unexpected error occurred while fetching equipment. Please try again later."}), 500

@equipment_bp.route('/add-entry', methods=['POST'])
def add_equipment_entry():
    """Adds an equipment entry to the session for the current reporting date."""
    try:
        current_date = session.get('report_date') or session.get('current_reporting_date')
        if not current_date:
            return jsonify({'error': 'No reporting date selected'}), 400

        # Initialize session storage
        daily_data = session.setdefault('daily_data', {})
        current_data = daily_data.setdefault(current_date, {})
        entries = current_data.setdefault('entries', {})
        equipment_entries = entries.setdefault('equipment', [])

        # Parse request data
        data = request.json
        equipment_name = data.get("equipmentName")
        labor_hours = data.get("laborHours")
        activity_code = data.get("activityCode")

        if not equipment_name or not labor_hours or not activity_code:
            return jsonify({"error": "All fields are required"}), 400

        # Ensure equipment is unique in session
        for existing_equipment in equipment_entries:
            if existing_equipment["equipmentName"] == equipment_name and existing_equipment["activityCode"] == activity_code:
                return jsonify({"error": f"Equipment '{equipment_name}' is already added to the session with the same activity."}), 400

        # Add to session storage
        equipment_entry = {
            "equipmentName": equipment_name,
            "laborHours": labor_hours,
            "activityCode": activity_code
        }

        equipment_entries.append(equipment_entry)
        session.modified = True

        return jsonify({"message": "Equipment added successfully", "equipment_entries": equipment_entries}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error adding equipment entry: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/create', methods=['POST'])
def create_equipment():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify(error='Name is required'), 400
    equip = Equipment(
        name=name,
        serial_number=data.get('serial_number'),
        maintenance_status=data.get('maintenance_status', 'operational')
    )
    db.session.add(equip)
    db.session.commit()
    return jsonify(message='Equipment created', id=equip.id), 201

@equipment_bp.route('/update/<int:equip_id>', methods=['PUT'])
def update_equipment(equip_id):
    equip = Equipment.query.get(equip_id)
    if not equip:
        return jsonify(error='Equipment not found'), 404
    data = request.get_json() or {}
    equip.name = data.get('name', equip.name)
    equip.serial_number = data.get('serial_number', equip.serial_number)
    equip.maintenance_status = data.get('maintenance_status', equip.maintenance_status)
    db.session.commit()
    return jsonify(message='Equipment updated'), 200

@equipment_bp.route('/delete/<int:equip_id>', methods=['DELETE'])
def delete_equipment(equip_id):
    equip = Equipment.query.get(equip_id)
    if not equip:
        return jsonify(error='Equipment not found'), 404
    db.session.delete(equip)
    db.session.commit()
    return jsonify(message='Equipment deleted'), 200