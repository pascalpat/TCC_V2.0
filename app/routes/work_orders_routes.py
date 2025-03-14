from flask import Blueprint, jsonify, request
import pandas as pd
import os

# Define the Blueprint for work orders
work_orders_bp = Blueprint('work_orders_bp', __name__, url_prefix='/work-orders')

# Path to the work orders data file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_ORDERS_FILE = os.path.join(BASE_DIR, '../../data/work_orders.csv')

@work_orders_bp.route('/list', methods=['GET'])
def get_work_orders():
    """
    Fetch and return the list of work orders from the CSV file.
    """
    try:
        # Check if the file exists
        if not os.path.exists(WORK_ORDERS_FILE):
            return jsonify({"status": "error", "message": "Work orders file not found"}), 404

        # Load the CSV file
        work_orders = pd.read_csv(WORK_ORDERS_FILE)

        # Check if the file is empty
        if work_orders.empty:
            return jsonify({"status": "success", "data": [], "message": "No work orders found"}), 200

        # Convert DataFrame to JSON format
        work_orders_list = work_orders.to_dict(orient='records')
        return jsonify({"status": "success", "data": work_orders_list}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"status": "error", "message": str(e)}), 500

@work_orders_bp.route('/add', methods=['POST'])
def add_work_order():
    """
    Add a new work order to the CSV file.
    """
    try:
        # Get the new work order data from the request
        new_work_order = request.json

        # Validate the input
        required_fields = ['order_number', 'description', 'hours']
        missing_fields = [field for field in required_fields if field not in new_work_order]
        if missing_fields:
            return jsonify({"status": "error", "message": f"Missing fields: {missing_fields}"}), 400

        # Check if the file exists, create it if not
        if not os.path.exists(WORK_ORDERS_FILE):
            work_orders = pd.DataFrame(columns=required_fields)
        else:
            work_orders = pd.read_csv(WORK_ORDERS_FILE)

        # Append the new work order
        work_orders = work_orders.append(new_work_order, ignore_index=True)

        # Save back to the CSV file
        work_orders.to_csv(WORK_ORDERS_FILE, index=False)
        return jsonify({"status": "success", "message": "Work order added successfully"}), 201

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"status": "error", "message": str(e)}), 500
