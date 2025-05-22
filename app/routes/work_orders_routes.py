from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models.work_orders_models import WorkOrder
from datetime import datetime

# Define the Blueprint for work orders
work_orders_bp = Blueprint('work_orders_bp', __name__, url_prefix='/work-orders')

def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, '%Y-%m-%d').date()
    except Exception:
        return None

@work_orders_bp.route('/list', methods=['GET'])
def get_work_orders():
    """Return all work orders from the database."""
    try:
        orders = WorkOrder.query.all()
        return jsonify({'work_orders': [o.to_dict() for o in orders]}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error loading work orders: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    
@work_orders_bp.route('/add', methods=['POST'])
def add_work_order():
    """Create a new work order record."""

    try:
        data = request.get_json() or {}
        required = ['project_id', 'sequential_number', 'description', 'type']
        if not all(data.get(f) for f in required):
            return jsonify({'error': 'Missing required fields'}), 400

        wo = WorkOrder(
            project_id=data['project_id'],
            sequential_number=data['sequential_number'],
            description=data['description'],
            type=data['type'],
            status=data.get('status', 'open'),
            reason=data.get('reason'),
            estimated_cost=data.get('estimated_cost'),
            subcontractor_id=data.get('subcontractor_id'),
            start_date=_parse_date(data.get('start_date')),
            expected_completion_date=_parse_date(data.get('expected_completion_date')),
            activity_code_id=data.get('activity_code_id'),
            activity_code=data.get('activity_code'),
        )

        db.session.add(wo)
        db.session.commit()
        return jsonify({'message': 'Work order created', 'data': wo.to_dict()}), 201



    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating work order: {e}", exc_info=True)
    return jsonify({'error': str(e)}), 500


@work_orders_bp.route('/update/<int:wo_id>', methods=['PUT'])
def update_work_order(wo_id):
    wo = WorkOrder.query.get(wo_id)
    if not wo:
        return jsonify(error='Work order not found'), 404
    data = request.get_json() or {}
    wo.description = data.get('description', wo.description)
    wo.status = data.get('status', wo.status)
    wo.reason = data.get('reason', wo.reason)
    db.session.commit()
    return jsonify(message='Work order updated'), 200


@work_orders_bp.route('/delete/<int:wo_id>', methods=['DELETE'])
def delete_work_order(wo_id):
    wo = WorkOrder.query.get(wo_id)
    if not wo:
        return jsonify(error='Work order not found'), 404
    db.session.delete(wo)
    db.session.commit()
    return jsonify(message='Work order deleted'), 200