from flask import Blueprint, jsonify, request, current_app
from .. import db  # Import the db object from your app package
from app.models.material_models import Material

materials_bp = Blueprint('materials_bp', __name__)

@materials_bp.route('/materials/list', methods=['GET'])
def get_materials():
    """
    Fetch and return the list of materials from the database
    """
    materials = Material.query.all()
    # Convert each DB row to a dictionary
    material_list = []
    for m in materials:
        material_list.append({
            "id": m.id,
            "name": m.name,
            "cos_per_unit": m.cost_per_unit,
            "unit": m.unit
        })
    return jsonify({"materials": material_list}), 200

@materials_bp.route('/materials/add', methods=['POST'])
def add_material():
    """
    Handle adding a new material.
    """
    data = request.json
    name = data.get('material_name')
    cost_per_unit = data.get('cost_per_unit')
    unit = data.get('unit')

    # Validate fields
    if not name or not cost_per_unit or not unit:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Create a new Material model instance
        new_material = Material(
            name=name,
            cost_per_unit=cost_per_unit,
            unit=unit
        )
        db.session.add(new_material)
        db.session.commit()

        return jsonify({"message": "Material added successfully!"}), 201
    except Exception as e:
        current_app.logger.error(f"Error adding material: {e}", exc_info=True)
        return jsonify({"error": "Failed to add material"}), 500