from flask import Blueprint, jsonify, current_app
from ..utils.data_loader import load_data
import os


pictures_bp = Blueprint('pictures_bp', __name__)

@pictures_bp.route('/pictures/list', methods=['GET'])
def get_pictures():
    """
    Fetch and return the list of pictures from the CSV file.
    """
    # 1. Retrieve the file path from config, or use a fallback
    pictures_file = current_app.config.get("PICTURES_FILE", "fallback_pictures.csv")
    abs_path = os.path.abspath(pictures_file)

    # 2. Check if the file even exists
    if not os.path.exists(abs_path):
        current_app.logger.info(f"No pictures CSV found at {abs_path}, returning empty list.")
        return jsonify({"pictures": []}), 200

    # 3. Attempt to load the CSV; columns can be adjusted as needed
    pictures_df = load_data(abs_path, columns=["filename", "description"])
    if pictures_df.empty:
        current_app.logger.info("Pictures CSV is empty or invalid, returning empty list.")
        return jsonify({"pictures": []}), 200
    
    # 4. If the DataFrame is empty, just return an empty list
    if pictures_df.empty:
        current_app.logger.info("Pictures CSV is empty or invalid, returning empty list.")
        return jsonify({"pictures": []}), 200

    # 5. Otherwise, convert DataFrame to a list of dicts for JSON response
    pictures_list = pictures_df.to_dict(orient="records")
    return jsonify({"pictures": pictures_list}), 200