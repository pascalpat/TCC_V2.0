from flask import Blueprint, jsonify, request
import pandas as pd
import os

# Define the Blueprint for daily notes
dailynotes_bp = Blueprint('dailynotes_bp', __name__, url_prefix='/dailynotes')

# Path to the daily notes data file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DAILYNOTES_FILE = os.path.join(BASE_DIR, '../../data/dailynotes.csv')

@dailynotes_bp.route('/list', methods=['GET'])
def get_daily_notes():
    """
    Fetch and return the list of daily notes from the CSV file.
    """
    try:
        # Check if the file exists
        if not os.path.exists(DAILYNOTES_FILE):
            return jsonify({"status": "error", "message": "Daily notes file not found"}), 404

        # Load the CSV file
        dailynotes = pd.read_csv(DAILYNOTES_FILE)

        # Check if the file is empty
        if dailynotes.empty:
            return jsonify({"status": "success", "data": [], "message": "No daily notes found"}), 200

        # Convert DataFrame to JSON format
        notes_list = dailynotes.to_dict(orient='records')
        return jsonify({"status": "success", "data": notes_list}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"status": "error", "message": str(e)}), 500

@dailynotes_bp.route('/add', methods=['POST'])
def add_daily_note():
    """
    Add a new daily note to the CSV file.
    """
    try:
        # Get the new note data from the request
        new_note = request.json

        # Validate the input
        if not new_note.get('content') or not new_note.get('date'):
            return jsonify({"status": "error", "message": "Missing required fields: 'content' and/or 'date'"}), 400

        # Check if the file exists, create it if not
        if not os.path.exists(DAILYNOTES_FILE):
            dailynotes = pd.DataFrame(columns=['content', 'date'])
        else:
            dailynotes = pd.read_csv(DAILYNOTES_FILE)

        # Append the new note
        dailynotes = dailynotes.append(new_note, ignore_index=True)

        # Save back to the CSV file
        dailynotes.to_csv(DAILYNOTES_FILE, index=False)
        return jsonify({"status": "success", "message": "Daily note added successfully"}), 201

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"status": "error", "message": str(e)}), 500
