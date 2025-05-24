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

    # Build a simple list of {id, name}
    result = [
        {'id': item.id, 'name': item.item_name}
        for item in items
    ]

    # Wrap it in a top‐level key if your front‐end expects it
    return jsonify(items=result), 200
