import pandas as pd
import csv
import logging
from flask import current_app

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


#DATA_FILE_PATH = "C:/Users/patri/OneDrive/Bureau/TCC_V2.0/data/daily_report_data.csv"
#DATA_FILE_PATH = current_app.config.get('DAILY_REPORT_DATA_FILE', 'default_fallback_path')

def load_data(file_path, columns=None, delimiter=None):
    """
    Load data from a CSV file and return a DataFrame.
    Supports optional column selection and delimiter detection.

    Parameters:
    - file_path (str): Path to the CSV file.
    - columns (list): List of columns to load (optional).
    - delimiter (str): Specific delimiter to use (optional).

    Returns:
    - pd.DataFrame: Loaded data as a DataFrame, or an empty DataFrame on failure.
    """
    # If no file path is passed in, read from current_app.config
    if file_path is None:
        file_path = current_app.config.get("DATA_FILE_PATH", "default_fallback.csv")

    delimiters = [',', ';', '\t'] if delimiter is None else [delimiter]

    for delim in delimiters:
        try:
            # Read the CSV into a DataFrame
            data = pd.read_csv(file_path, delimiter=delim)
            logger.debug(f"Data loaded successfully from {file_path} with delimiter '{delim}'")
            
            data.columns = data.columns.str.strip()  # Strip whitespace from column names
            if columns:
                data = data[columns]
            #print(f"Data loaded successfully from {file_path} with delimiter '{delim}'")
            logger.info(f"Data loaded successfully from {file_path} with delimiter '{delim}'")
            return data
        except ValueError as ve:
            #print(f"ValueError with delimiter '{delim}': {ve}")
            logger.debug(f"ValueError with delimiter '{delim}': {ve}")   
        except FileNotFoundError:
            #print(f"Error: File {file_path} not found.")
            logger.warning(f"Error: File {file_path} not found.")
            break
        except Exception as e:
            #print(f"Error reading file {file_path} with delimiter '{delim}': {e}")
            logger.warning(f"Failed to read file {file_path} with any delimiter.") 
        #print(f"Failed to read file {file_path} with any delimiter.")
        logger.warning(f"Failed to read file {file_path} with any delimiter.") 
    return pd.DataFrame()  # Return an empty DataFrame if all attempts fail

def save_to_csv(session_data, date, file_path=None):
    """
    Transfer session data to the consolidated CSV file.

    Parameters:
    - session_data (dict): The session dictionary containing tab data for the given date.
    - date (str): The date for which the data should be saved.
    """

    if file_path is None:
        # Fall back to config if no explicit path is passed
        file_path = current_app.config.get("DATA_FILE_PATH", "default_fallback.csv")

    headers = [
        "dateStamp", "dateEntered", "projectId", "tabType", "activityCode",
        "workerName", "laborHours", "equipmentName", "equipmentHours", "materialName",
        "materialQuantity", "unit", "subcontractorName", "subcontractorCost",
        "workOrderId", "description", "cost", "approvalStatus",
        "workOrderPictureName", "workOrderPicturePath", "workOrderPdfName",
        "workOrderPdfPath", "pictureName", "filePath", "pictureType", "latitude",
        "longitude", "imageTimestamp", "deviceMake", "deviceModel", "orientation",
        "width", "height", "notes", "createdAt", "enteredBy"
    ]

    rows = []
    for tab_type, entries in session_data[date].items():
        if isinstance(entries, list):  # Handle tab data stored as lists
            for entry in entries:
                entry_data = {
                    "dateStamp": date,
                    "dateEntered": "",  # Optional: Add current date/time here
                    **entry,  # Merge the session entry into row data
                    "tabType": tab_type  # Add tab type for this entry
                }
                rows.append(entry_data)

    try:
        with open(file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if file.tell() == 0:  # Write headers if file is new
                writer.writeheader()
            writer.writerows(rows)
        #print(f"Session data for {date} saved to {DATA_FILE_PATH}")
        logger.info(f"Session data for {date} saved to {file_path}")   
    except Exception as e:
        #print(f"Error saving session data to CSV: {e}")
        logger.info(f"Error saving session data to CSV: {e}")   