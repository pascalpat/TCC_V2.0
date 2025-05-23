from flask import Blueprint, request, jsonify
from app import db
from app.models.purchase_order_models import PurchaseOrder

purchase_orders_bp = Blueprint('purchase_orders_bp', __name__, url_prefix='/purchase-orders')

@purchase_orders_bp.route('/list', methods=['GET'])
def list_purchase_orders():
    orders = PurchaseOrder.query.all()
    order_list = [
        {
            'id': o.id,
            'order_number': o.order_number,
            'vendor': o.vendor,
            'total_cost': o.total_cost,
            'on_site_status': o.on_site_status
        }
        for o in orders
    ]
    return jsonify(purchase_orders=order_list), 200

@purchase_orders_bp.route('/create', methods=['POST'])
def create_purchase_order():
    data = request.get_json() or {}
    order_number = data.get('order_number')
    vendor = data.get('vendor')
    if not order_number or not vendor:
        return jsonify(error='Missing required fields'), 400
    po = PurchaseOrder(
        order_number=order_number,
        vendor=vendor,
        vendor_address=data.get('vendor_address'),
        total_cost=data.get('total_cost'),
        on_site_status=data.get('on_site_status', 'pending'),
        project_id=data.get('project_id')
    )
    db.session.add(po)
    db.session.commit()
    return jsonify(message='Purchase order created', id=po.id), 201

@purchase_orders_bp.route('/update/<int:po_id>', methods=['PUT'])
def update_purchase_order(po_id):
    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify(error='Purchase order not found'), 404
    data = request.get_json() or {}
    po.vendor = data.get('vendor', po.vendor)
    po.total_cost = data.get('total_cost', po.total_cost)
    po.on_site_status = data.get('on_site_status', po.on_site_status)
    db.session.commit()
    return jsonify(message='Purchase order updated'), 200

@purchase_orders_bp.route('/delete/<int:po_id>', methods=['DELETE'])
def delete_purchase_order(po_id):
    po = PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify(error='Purchase order not found'), 404
    db.session.delete(po)
    db.session.commit()
    return jsonify(message='Purchase order deleted'), 200