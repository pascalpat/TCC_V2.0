from flask import Flask, jsonify, request
from flask import Blueprint
from app.utils.validation import validate_worker_input
from app.routes.data_persistence import save_to_csv
from flask import session, current_app
import logging

app = Flask(__name__)

# Create the blueprint
update_progress_bp = Blueprint('update_progress', __name__, url_prefix='/update-progress')

# Global variable for simplicity; replace with a more persistent storage if needed
TOTAL_TABS = 7

def mark_tab_completed(tab_name):
    """Mark a tab as completed and update progress."""
    try:
        current_date = session.get('report_date') or session.get('current_reporting_date')
        if not current_date:
            logging.error("No reporting date in session.")
            return {'error': 'No reporting date in session'}, 400

        # Ensure daily_data exists
        daily_data = session.setdefault('daily_data', {})
        current_data = daily_data.setdefault(current_date, {})
        tab_statuses = current_data.setdefault('tab_statuses', {})  # Ensure tab_statuses exists

        # Mark the tab as completed
        tab_statuses[tab_name] = 'completed'

        # Calculate progress percentage
        completed_tabs = sum(1 for status in daily_data[current_date]['tab_statuses'].values() if status == 'completed')
        total_tabs = len(daily_data[current_date]['tab_statuses'])
        progress_percentage = int((completed_tabs / total_tabs) * 100)

        session['daily_data'] = daily_data
        session.modified = True

        logging.info(f"Tab '{tab_name}' marked as completed. Progress: {progress_percentage}%")
        return {'progressPercentage': progress_percentage}
    except Exception as e:
        logging.error(f"Error marking tab {tab_name} as completed: {e}", exc_info=True)
        return {'error': str(e)}

@update_progress_bp.route('/update-progress', methods=['POST'])
def update_progress():
    """
    Update progress for a specific tab.
    """
    data = request.get_json()
    tab_name = data.get('tab')

    if not tab_name:
            return jsonify({'error': 'Tab name is required'}), 400

    result = mark_tab_completed(tab_name)

    return jsonify(result), 200
    
    

@update_progress_bp.route('/get-completed-tabs', methods=['GET'])
def get_completed_tabs():
    """
    Get the list of completed tabs and progress percentage.
    """
    completed_tabs = session.get('completedTabs', [])
    progress_percentage = (len(completed_tabs) / TOTAL_TABS) * 100 if completed_tabs else 0
   
    return jsonify({
        'completedTabs': completed_tabs,
        'progressPercentage': progress_percentage
    }), 200

@update_progress_bp.route('/reset-progress', methods=['POST'])
def reset_progress():
    """
    Endpoint to reset all progress by clearing completed tabs.
    """
    session.pop('completedTabs', None)  # Remove the completedTabs from session
    return jsonify({"message": "Progress reset successfully"}), 200

@update_progress_bp.route('/check-all-tabs-completed', methods=['GET'])
def check_all_tabs_completed():
    try:
        current_date = session.get('report_date') or session.get('current_reporting_date')
        daily_data = session.get('daily_data', {})

        if not current_date or current_date not in daily_data:
            return jsonify({'allTabsCompleted': False}), 200

        all_tabs_completed = all(
            status == 'completed' for status in daily_data[current_date]['tab_statuses'].values()
        )

        return jsonify({'allTabsCompleted': all_tabs_completed}), 200
    except Exception as e:
        logging.error(f"Error checking tab completion status: {e}")
        return jsonify({'error': str(e)}), 500

@update_progress_bp.route('/get-progress', methods=['GET'])
def get_progress():
    """
    Get the progress percentage and list of completed tabs.
    """
    try:
        # Retrieve session data
        current_date = session.get('report_date') or session.get('current_reporting_date')
        daily_data = session.get('daily_data', {})

        if not current_date or current_date not in daily_data:
            return jsonify({'progressPercentage': 0, 'completedTabs': []}), 200

        tab_statuses = daily_data[current_date].get('tab_statuses', {})
        completed_tabs = [tab for tab, status in tab_statuses.items() if status == 'completed']
        progress_percentage = (len(completed_tabs) / TOTAL_TABS) * 100 if TOTAL_TABS else 0

        current_app.logger.debug(f"Progress data: {progress_percentage}, {completed_tabs}")

        return jsonify({
            'progressPercentage': round(progress_percentage, 2),
            'completedTabs': completed_tabs
        }), 200
    except Exception as e:
        logging.error(f"Error fetching progress data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
