# app/routes/payment_items_routes.py

from flask import Blueprint, jsonify
from app import db
from app.models.core_models import PaymentItem  # PaymentItem lives here :contentReference[oaicite:0]{index=0}

payment_items_bp = Blueprint(
    'payment_items',            # blueprint name
    __name__,
    url_prefix='/payment-items' # so routes are under /payment-items/...
)

@payment_items_bp.route('/list', methods=['GET'])
def list_payment_items():
    """
    Return JSON for populating a dropdown of payment items.
    """
    # Query all payment items, ordered by the item name
    items = PaymentItem.query.order_by(PaymentItem.item_name).all()

    # Convert the query result to a list of dictionaries
    # Each dictionary contains the id, payment_code, and item_name of the payment item
    return jsonify({
        'payment_items': [
            {
                'id': item.id,
                'payment_code': item.payment_code,
                'item_name': item.item_name
            }
            for item in items
        ]
    }), 200
