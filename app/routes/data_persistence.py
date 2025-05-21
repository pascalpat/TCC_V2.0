from flask import Blueprint, session, jsonify, request, current_app
from app.utils.data_loader import load_data
import csv
from datetime import datetime
import os


data_persistence_bp = Blueprint('data_persistence', __name__)


# Function to save session data to a permanent file
def persist_session_to_csv(session_data, current_date, csv_file_path):
    try:
        if current_date not in session_data:
            raise ValueError("No data available for the selected reporting date.")

        daily_data = session_data[current_date]
        entries = []
        for tab, data in daily_data['data'].items():
            for entry in data:
                entry['dateStamp'] = current_date
                entry['dateEntered'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                entry['tabType'] = tab
                entries.append(entry)

        fieldnames = [
            "dateStamp", "dateEntered", "projectId", "tabType", "activityCode", "workerName",
            "laborHours", "equipmentName", "equipmentHours", "materialName", "materialQuantity",
            "unit", "subcontractorName", "subcontractorCost", "workOrderId", "description",
            "cost", "approvalStatus", "workOrderPictureName", "workOrderPicturePath",
            "workOrderPdfName", "workOrderPdfPath", "pictureName", "filePath", "pictureType",
            "latitude", "longitude", "imageTimestamp", "deviceMake", "deviceModel", "orientation",
            "width", "height", "notes", "createdAt", "enteredBy"
        ]

        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            for entry in entries:
                writer.writerow(entry)

        return {"status": "success", "message": "Data saved successfully."}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Define the default path to the CSV file. This path mirrors the default used
# in the application's configuration and serves as a fallback if the
# `DATA_FILE_PATH` configuration variable is not set.
default_data_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'daily_report_data.csv')
)





# Route to save report
@data_persistence_bp.route('/save-report', methods=['POST'])
def save_to_csv():
    current_date = session.get('report_date') or session.get('current_reporting_date')

    if not current_date or current_date not in session['daily_data']:
        return jsonify({'error': 'No data available to save.'}), 400

    # Fetch data for the current date
    daily_data = session['daily_data'][current_date]

    # Flatten the session data into a row-based format
    rows = []
    for tab, entries in daily_data['data'].items():
        for entry in entries:
            row = {
                'dateStamp': current_date,
                'tabType': tab,
                # Add more columns as necessary based on your session data
                **entry
            }
            rows.append(row)

    # Determine the CSV file path from configuration with a sensible fallback
    data_file_path = current_app.config.get('DATA_FILE_PATH', default_data_path)

    # Save rows to the CSV using the resolved path
    save_to_csv(data_file_path, rows, append=True)



    # Clear session data for the saved date
    session['daily_data'].pop(current_date)
    session.modified = True

    return jsonify({'message': 'Report saved successfully!', 'status': 'success'})