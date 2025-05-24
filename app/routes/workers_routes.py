# app/routes/workers_routes.py

# app/routes/workers_routes.py

from flask import Blueprint, request, jsonify, session, current_app
import logging
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.workforce_models import Worker
from app.routes.update_progress_routes import mark_tab_completed

# Define the Blueprint for worker-related routes
workers_bp = Blueprint('workers_bp', __name__, url_prefix='/workers')


# Logging Configuration
logging.basicConfig(level=logging.INFO)

# Define allowed roles
VALID_ROLES = {"admin", "manager", "superintendent", "foreman", "worker"}

@workers_bp.route('/list', methods=['GET'])
def get_workers_list():
    """Fetch the list of valid workers from the database."""
    try:
        workers = Worker.query.all()
        logging.info(f"Fetched {len(workers)} workers from the database.")

        # Validate and filter only workers with valid fields
        valid_workers = [
            {'id': worker.id, 'name': worker.name}
            for worker in workers if worker.id and worker.name
        ]

        return jsonify({'workers': valid_workers}), 200

    except SQLAlchemyError as e:
        logging.error(f"Database error fetching workers: {str(e)}", exc_info=True)
        return jsonify({'error': "Database error while fetching workers"}), 500
    except Exception as e:
        logging.error(f"Unexpected error fetching workers: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@workers_bp.route('/add-worker', methods=['POST'])
def add_worker():
    """
    Adds a worker to the database and session for the current reporting date.
    """
    try:
        current_date = session.get('report_date') or session.get('current_reporting_date')
        if not current_date:
            return jsonify({'error': 'No reporting date selected'}), 400

        # Initialize daily session data
        daily_data = session.setdefault('daily_data', {})
        current_data = daily_data.setdefault(current_date, {})
        entries = current_data.setdefault('entries', {})
        workers = entries.setdefault('workers', [])
        tab_statuses = current_data.setdefault('tab_statuses', {})

        # Parse and validate incoming data
        data = request.json
        logging.info(f"Received worker data: {data}")

        if not data:
            return jsonify({"error": "No data provided"}), 400

        worker_name = data.get("workerName")
        labor_hours = data.get("laborHours")
        activity_code = data.get("activityCode")
        role = data.get("role", "worker").lower()  # Default to 'worker'

        # Input validation
        if not worker_name or not labor_hours or not activity_code:
            return jsonify({"error": "Worker name, labor hours, and activity code are required"}), 400

        if role not in VALID_ROLES:
            return jsonify({"error": f"Invalid role '{role}'. Allowed roles: {', '.join(VALID_ROLES)}"}), 400

        try:
            labor_hours = float(labor_hours)
            if labor_hours <= 0:
                return jsonify({"error": "Labor hours must be a positive number"}), 400
        except ValueError:
            return jsonify({"error": "Invalid number for labor hours"}), 400

        # Ensure worker is unique in session
        for existing_worker in workers:
            if existing_worker["workerName"] == worker_name and existing_worker["activityCode"] == activity_code:
                return jsonify({"error": f"Worker '{worker_name}' is already added to the session with the same activity."}), 400

        # Check if worker already exists in DB
        existing_worker = Worker.query.filter_by(name=worker_name).first()
        if not existing_worker:
            # Add new worker to database if not found
            new_worker = Worker(name=worker_name, role=role)
            db.session.add(new_worker)
            db.session.commit()
            logging.info(f"Worker '{worker_name}' added to database.")

        # Add worker details to session
        worker_entry = {
            "workerName": worker_name,
            "laborHours": labor_hours,
            "activityCode": activity_code,
            "role": role,
            "status": "new"
        }

        workers.append(worker_entry)
        session.modified = True  # ✅ Ensure session updates persist

        return jsonify({"message": "Worker added successfully", "workers": workers}), 200

    except SQLAlchemyError as e:
        logging.error(f"Database error in add_worker: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({"error": "Database error occurred while adding worker"}), 500
    except Exception as e:
        logging.error(f"Unexpected error in add_worker: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
@workers_bp.route('/update/<int:worker_id>', methods=['PUT'])
def update_worker(worker_id):
    worker = Worker.query.get(worker_id)
    if not worker:
        return jsonify(error='Worker not found'), 404
    data = request.get_json() or {}
    worker.name = data.get('name', worker.name)
    worker.role = data.get('role', worker.role)
    db.session.commit()
    return jsonify(message='Worker updated'), 200


@workers_bp.route('/delete/<int:worker_id>', methods=['DELETE'])
def delete_worker(worker_id):
    worker = Worker.query.get(worker_id)
    if not worker:
        return jsonify(error='Worker not found'), 404
    db.session.delete(worker)
    db.session.commit()
    return jsonify(message='Worker deleted'), 200   

@workers_bp.route('/confirm-workers', methods=['POST'])
def confirm_workers():
    """
    Confirms workers for the current reporting date and updates session data.
    """
    try:
        current_date = session.get('report_date') or session.get('current_reporting_date')
        if not current_date:
            return jsonify({'error': 'No reporting date selected'}), 400

        daily_data = session.setdefault('daily_data', {})
        current_data = daily_data.setdefault(current_date, {})
        entries = current_data.setdefault('entries', {})
        workers = entries.setdefault('workers', [])
        tab_statuses = current_data.setdefault('tab_statuses', {})

        # Parse the incoming JSON payload
        data = request.get_json()
        if not data or 'workers' not in data:
            return jsonify({'error': 'Invalid or missing workers data'}), 400

        new_workers = data['workers']

        # Mark workers as confirmed
        for worker in new_workers:
            for existing_worker in workers:
                if (
                    worker['workerName'] == existing_worker['workerName']
                    and worker['laborHours'] == existing_worker['laborHours']
                    and worker['activityCode'] == existing_worker['activityCode']
                ):
                    existing_worker['status'] = 'confirmed'

        session.modified = True

        # Mark the workers tab as completed
        progress_data = mark_tab_completed('workers')
        if 'error' in progress_data:
            logging.error(f"Error in mark_tab_completed: {progress_data}")
            return jsonify(progress_data), 400

        logging.info(f"Workers confirmed for {current_date}. Updated session data: {session.get('daily_data')}")
        return jsonify({'message': 'Workers confirmed successfully!', 'status': 'success', **progress_data}), 200

    except Exception as e:
        logging.error(f"Error in confirm_workers: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@workers_bp.route('/session-list', methods=['GET'])
def get_session_workers():
    """Fetch workers from the session for the current reporting date."""
    try:
        current_date = session.get('report_date') or session.get('current_reporting_date')
        if not current_date:
            return jsonify({'error': 'No reporting date in session'}), 400

        daily_data = session.get('daily_data', {})
        workers = daily_data.get(current_date, {}).get('entries', {}).get('workers', [])
        logging.info(f"Fetched workers for {current_date}: {workers}")
        return jsonify({'workers': workers}), 200
    except Exception as e:
        logging.error(f"Error fetching session workers: {e}")
        return jsonify({'error': str(e)}), 500


@workers_bp.route('/reset-session', methods=['POST', 'GET'])
def reset_session():
    """Clear the current session."""
    session.clear()
    logging.info("Session has been cleared.")
    return jsonify({"message": "Session reset successfully."}), 200

