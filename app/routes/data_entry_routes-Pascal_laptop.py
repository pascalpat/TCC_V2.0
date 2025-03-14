# app/routes/data_entry_routes.py
from flask import Blueprint, request, session, jsonify, flash, redirect, url_for, render_template, current_app
import logging
from datetime import datetime
import openpyxl
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app.utils.data_loader import load_data  # Import the load_data function

data_entry_bp = Blueprint('data_entry_bp', __name__, url_prefix='/data_entry')

UPLOAD_FOLDER = "C:\\Users\\patri\\OneDrive\\Bureau\\TCC_V2.0\\uploads"
EQUIPMENT_FILE = "C:\\Users\\patri\\OneDrive\\Bureau\\TCC_V2.0\\data\\equipment.csv"
UPLOAD_FOLDER = "C:\\Users\\patri\\OneDrive\\Bureau\\TCC_V2.0\\uploads"

def validate_date(date_string):
    """Validate if the date string is in 'YYYY-MM-DD' format."""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
@data_entry_bp.route('/initialize-day', methods=['POST'])
def initialize_day():
    """Initialize session data for the selected reporting day."""
    print("sartting: @data_entry_bp.route('/initialize-day', methods=['POST'])")
    try:
        data = request.get_json()
        date_stamp = data.get('dateStamp')
        

        if not date_stamp:
            return jsonify({'status': 'error', 'message': 'No date provided'}), 400

        # Initialize daily_data in session
        daily_data = session.get('daily_data', {})
        if date_stamp not in daily_data:
            daily_data[date_stamp] = {
                'tab_statuses': {tab: 'incomplete' for tab in ['Workers', 'Materials', 'Equipment', 'Subcontractors', 'DailyNotes', 'WorkOrders', 'Pictures']},
                'entries': {}  # Placeholder for actual data
            }
            session['daily_data'] = daily_data
            session['current_reporting_date'] = date_stamp
            session.modified = True

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logging.error(f"Error initializing day: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route: Get completed and in-progress days
@data_entry_bp.route('/days-status', methods=['GET'])
def get_days_status():
    """Return completed and in-progress days for the calendar."""
    try:
        daily_data = session.get('daily_data', {})
        completed_days = []
        in_progress_days = []

        
        for date_stamp, tabs in daily_data.items():
            statuses = [tab['status'] for tab in tabs.values()]
            if all(status == 'completed' for status in statuses):
                completed_days.append(date_stamp)
            else:
                in_progress_days.append(date_stamp)

        # Return empty arrays if no data is found
        return jsonify({
            'completedDays': completed_days or [],
            'incompleteDays': in_progress_days or []
        }), 200
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'message': 'Error retrieving day statuses',
            'error': str(e),
            'completedDays': [],
            'incompleteDays': []
        }), 500

@data_entry_bp.route('/submit_data_entry', methods=['GET', 'POST'])
def submit_data_entry():
    #"""
    #Handle data entry for the daily report. Processes data from multiple tabs,
    #validates it, and stores it in the appropriate format.
    #"""
    try:
        current_app.logger.info("Data_entry function called.")
        # -----------------
        # STEP 1: Validate session and project info
        # -----------------
        project_number = session.get('project_number') or request.form.get('projectNumber')
        report_date = session.get('current_reporting_date')

        # Validate project and report date
        if not project_number or not report_date:
            flash('Project ID or Report Date is missing. Please select a project and date.', 'danger')
            return redirect(url_for('calendar_bp.calendar_page'))
        
        # Store project number in session if not already set
        if 'project_number' not in session:
            session['project_number'] = project_number
            session.modified = True
            print(f"Project number set in session: {session['project_number']}")

        if 'current_reporting_date' not in session:
            session['current_reporting_date'] = report_date
            session.modified = True
            print(f"Report date set in session: {session['current_reporting_date']}")

        # -----------------
        # STEP 2 (POST logic only): Collect form data if we're saving
        # -----------------
        # 4. Load equipment data (still CSV or DB)
        # 3. Placeholder for collecting form data
        form_data = collect_form_data('worker', ['workerName', 'laborHours', 'activityCode'], 100)
        work_orders = collect_work_orders(100, UPLOAD_FOLDER)
        daily_pictures = collect_daily_pictures(request.files)
        equipment_data = load_data(EQUIPMENT_FILE, ['equipment_name'])  

        # Save everything (Excel, CSV, or DB). 
        # Adjust arguments if your `save_data_to_excel` signature differs.
        save_data_to_excel(
            workers_data=form_data,
            work_orders_data=work_orders,
            pictures_of_the_day=daily_pictures,
            equipment_data=equipment_data,
            project_number=project_number,
            general_notes=request.form.get('generalNotes', ''),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        current_app.logger.info("Data has been saved successfully!")
        flash("Data has been saved successfully!", "success")
        
        # -----------------
        # STEP 3: Render a template (GET or after POST)
        # -----------------
        
        # Render the index_old.html with the active project and report date
        return render_template('index_old.html', project_id=project_number, report_date=report_date)

    except Exception as e:
        logging.error(f"Error in submit_data_entry: {e}", exc_info=True)
        flash("An unexpected error occurred. Please try again.", 'danger')
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
@data_entry_bp.route('/report', methods=['POST'])
def redirect_to_data_entry():
    """
    Handle form submission from the calendar page.
    """
    try:
        # Extract date and project from the form
        report_date = request.form.get('report_date')
        project_id = request.form.get('project_id')

        # Validate the input
        if not report_date or not project_id:
            flash('Both date and project must be selected.')
            return redirect(url_for('calendar_bp.calendar_page'))  # Redirect to the calendar page if validation fails

        # Store in session for use in the data entry page
        session['current_reporting_date'] = report_date
        session['project_number'] = project_id

        print(f"Redirecting to data entry page with Date: {report_date}, Project: {project_id}")

        # Redirect to the data entry page
        return redirect(url_for('data_entry_bp.submit_data_entry'))

    except Exception as e:
        logging.error(f"Error in redirect_to_data_entry: {e}")
        flash("An error occurred while processing your request. Please try again.")
        return redirect(url_for('calendar_bp.calendar_page'))

@data_entry_bp.route('/reset-session', methods=['POST'])
def reset_session():
    """
    Reset the current project and report date selection in the session.
    """
    try:
        session.pop('project_number', None)
        session.pop('current_reporting_date', None)
        session.modified = True
        return jsonify({"message": "Session reset successfully."}), 200
    except Exception as e:
        logging.error(f"Error resetting session: {e}")
        return jsonify({"error": "Failed to reset session."}), 500 
    
    
def collect_form_data(prefix, fields, max_count):
    data_list = []

    #Ensure prefix is accessed and used, even if empty
    prefix = prefix or ''

    for i in range(1, max_count + 1):
        entry = {}
        valid_entry = False
        
        for field in fields:
            field_name = f"{field}_{i}"
            field_value = request.form.get(field_name)
            if field_value:
                entry[field] = field_value
                valid_entry = True
        if valid_entry:
            data_list.append(entry)
    return data_list

def collect_work_orders(max_count, upload_folder):
    work_orders = []
    for i in range(1, max_count + 1):
        #fetch form data
        work_order_name = request.form.get(f'workOrderName_{i}')
        activity_code = request.form.get(f'workOrderCode_{i}')
        work_order_signed = request.files.get(f'workOrderSigned_{i}')
        work_order_pictures = request.files.getlist(f'workOrderPictures_{i}')

        #validate the required fields
        if work_order_name and activity_code:
            work_order_entry = {
                'Work Order Name': work_order_name,
                'Activity Code': activity_code,
                'Signed Work Order': None,
                'Pictures': []
            }

            # Save signed work order file if exists
            if work_order_signed and work_order_signed.filename:
                try:
                    filename = secure_filename(work_order_signed.filename)
                    save_path = os.path.join(upload_folder, filename)
                    work_order_signed.save(save_path)
                    work_order_entry['Signed Work Order'] = filename
                except Exception as e:
                    print(f"Failed to save signed work order: {e}")
                    flash("Failed to save signed work order.", "danger")
                    
            # Save associated pictures
            for picture in work_order_pictures:
                if picture and picture.filename:
                    try:
                        pic_filename = secure_filename(picture.filename)
                        pic_save_path = os.path.join(upload_folder, pic_filename)
                        picture.save(pic_save_path)
                        work_order_entry['Pictures'].append(pic_filename)
                    except Exception as e:
                        print(f"Failed to save work order picture: {e}")
                        flash("Failed to save work order picture.", "danger")

            work_orders.append(work_order_entry)
    return work_orders

def collect_daily_pictures():
    pictures_of_the_day = []
    daily_pictures = request.files.getlist('dailyPictures')
    daily_picture_notes = request.form.get('dailyPictureNotes', '')

    for picture in daily_pictures:
        if picture:
            pic_filename = secure_filename(picture.filename)
            picture.save(UPLOAD_FOLDER / pic_filename)
            pictures_of_the_day.append({
                'Picture': pic_filename,
                'Notes': daily_picture_notes
            })
    return pictures_of_the_day

def save_data_to_excel(workers_data=None, materials_data=None, equipment_data=None, subcontractors_data=None, work_orders_data=None, pictures_of_the_day=None, general_notes=None, project_number=None, timestamp=None):
    file_path = f'C:\\Users\\patri\\OneDrive\\Bureau\\TCC_V2.0\\project_data_{project_number}.xlsx'

    try:
        # Load the existing workbook or create a new one if it does not exist
        try:
            book = openpyxl.load_workbook(file_path)
        except FileNotFoundError:
            book = openpyxl.Workbook()
            book.save(file_path)

        # Get the current date and time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Helper function to append data to a sheet
        def append_to_sheet(writer, new_data, sheet_name):
            try:
                # Load existing data from the sheet if it exists
                existing_df = pd.read_excel(file_path, sheet_name=sheet_name)
                # Add date tag to new data
                for entry in new_data:
                    entry['date_tag'] = current_time
                    entry['project_number'] = project_number
                # Concatenate the old and new data
                combined_df = pd.concat([existing_df, pd.DataFrame(new_data)], ignore_index=True)
            except ValueError:  # If sheet doesn't exist, just use new data
                # Add date tag to new data
                for entry in new_data:
                    entry['date_tag'] = current_time
                    entry['project_number'] = project_number
                combined_df = pd.DataFrame(new_data)
            
            # Write the combined data back to the Excel file            
            combined_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Use ExcelWriter to append new data
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            if workers_data:
                append_to_sheet(writer, workers_data, 'Workers')

            if materials_data:
                append_to_sheet(writer, materials_data, 'Materials')

            if equipment_data:
                append_to_sheet(writer, equipment_data, 'Equipment')

            if subcontractors_data:
                append_to_sheet(writer, subcontractors_data, 'Subcontractors')

            if work_orders_data:
                append_to_sheet(writer, work_orders_data, 'Work Orders')

            if pictures_of_the_day:
                append_to_sheet(writer, pictures_of_the_day, 'Pictures of the Day')

            if general_notes:
                append_to_sheet(writer, [{'General Notes': general_notes}], 'General Notes')

        print(f"Data appended to Excel file: {file_path}")

    except Exception as e:
        print(f"Failed to save data tp excel: {e}")
    