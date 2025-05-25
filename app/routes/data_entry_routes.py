# app/routes/data_entry_routes.py
from flask import Blueprint, request, session, jsonify, flash, redirect, url_for, render_template, current_app
from app.models.workforce_models import Worker
from app.models.core_models import ActivityCode, PaymentItem, CWPackage, Project
import logging
from app.models import DailyNoteEntry
from datetime import datetime
import openpyxl
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app.utils.data_loader import load_data  # Import the load_data function

data_entry_bp = Blueprint('data_entry_bp', __name__, url_prefix='/data-entry')

    
@data_entry_bp.route('/initialize-day', methods=['POST'])
def initialize_day():
    """Initialize session data for the selected reporting day."""
    try:
        data = request.get_json()
        date_stamp = data.get('dateStamp')
        

        if not date_stamp:
            return jsonify({'status': 'error', 'message': 'No date provided'}), 400

        # Initialize daily_data in session
        daily_data = session.get('daily_data', {})
        if date_stamp not in daily_data:
            daily_data[date_stamp] = {
                'tab_statuses': {tab: 'incomplete' for tab in ['Workers', 'Materials', 'Equipment', 'Subcontractors', 'DailyNoteEntry', 'WorkOrders', 'Pictures']},
                'entries': {}  # Placeholder for actual data
            }
            session['daily_data'] = daily_data
            # store under new unified key
            session['report_date'] = date_stamp
            # keep legacy key for backward compatibility
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

        # each value in daily_data is a dict with keys 'tab_statuses' and 'entries'
        for date_stamp, info in daily_data.items():
            tab_statuses = info.get('tab_statuses', {})
            statuses = list(tab_statuses.values())
            if statuses and all(s == 'completed' for s in statuses):
                completed_days.append(date_stamp)
            else:
                in_progress_days.append(date_stamp)

        return jsonify({
            'completedDays': completed_days,
            'incompleteDays': in_progress_days
        }), 200
        
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'message': 'Error retrieving day statuses',
            'error': str(e),
            'completedDays': [],
            'incompleteDays': []
        }), 500

# ──────────────────────────────────────────────────────────────────────────────
#   1) Your existing GET for the main data-entry page, with cwps fixed
# ──────────────────────────────────────────────────────────────────────────────
@data_entry_bp.route('/submit_data_entry', methods=['GET', 'POST'])
def submit_data_entry():
    current_app.logger.info("Data_entry function called.")
    
    project_number = session.get('project_id') or session.get('project_number')
    report_date    = session.get('report_date') or session.get('current_reporting_date')

    # resolve numeric PK from the project_number
    project = Project.query.filter_by(project_number=project_number).first()
    if project is None:
        flash("Projet introuvable !", "danger")
        return redirect(url_for('calendar_bp.calendar_page'))

    # now query by project.id for **all three** lists
    activity_codes = ActivityCode.query.filter_by(project_id=project.id).all()
    payment_items  = PaymentItem.   query.filter_by(project_id=project.id).all()
    cwps = CWPackage.query.filter_by(project_id=project_number).all()

    current_datetime = datetime.utcnow().isoformat(timespec="minutes")

    return render_template(
        'data_entry.html',
        project_id=project_number,
        report_date=report_date,
        activity_codes=activity_codes,
        payment_items=payment_items,
        cwps=cwps,
        current_datetime=current_datetime,
    )

# ──────────────────────────────────────────────────────────────────────────────
#   2) New JSON endpoint for payments
# ──────────────────────────────────────────────────────────────────────────────
@data_entry_bp.route('/payment-items/list', methods=['GET'])
def list_payment_items():
    project_number = session.get('project_id') or session.get('project_number')
    project = Project.query.filter_by(project_number=project_number).first()
    items = PaymentItem.query.filter_by(project_id=project.id).all()
    return jsonify({
        'payment_items': [
            {'id': i.id, 'payment_code': i.payment_code, 'item_name': i.item_name}
            for i in items
        ]
    })

# ──────────────────────────────────────────────────────────────────────────────
#   3) New JSON endpoint for CW-packages
# ──────────────────────────────────────────────────────────────────────────────
@data_entry_bp.route('/cw-packages/list', methods=['GET'])
def list_cwps():
    project_number = session.get('project_id') or session.get('project_number')
    #project = Project.query.filter_by(project_number=project_number).first()
    cwps = CWPackage.query.filter_by(project_id=project_number).all()
    return jsonify({
        'cwps': [
            {'code': c.code, 'name': c.name}
            for c in cwps
        ]
    })

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
        session['report_date'] = report_date
        session['project_id'] = project_id
        # Keep legacy keys for backward compatibility
        session['current_reporting_date'] = report_date
        session['project_number'] = project_id

        current_app.logger.debug(f"Redirecting to data entry page with Date: {report_date}, Project: {project_id}")

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
        session.pop('project_id', None)
        session.pop('report_date', None)
        # Remove legacy keys as well
        session.pop('project_number', None)
        session.pop('current_reporting_date', None)
        session.modified = True
        return jsonify({"message": "Session reset successfully."}), 200
    except Exception as e:
        logging.error(f"Error resetting session: {e}")
    return jsonify({"error": "Failed to reset session."}), 500


@data_entry_bp.route('/save_draft', methods=['POST'])
def save_draft():
    """Persist tab entries into the session as a draft."""
    try:
        data = request.get_json() or {}
        tab = data.get('tab')
        entries = data.get('entries', [])

        if not tab:
            return jsonify({'error': 'Tab is required'}), 400

        current_date = session.get('report_date') or session.get('current_reporting_date')

        if not current_date:
            return jsonify({'error': 'No reporting date selected'}), 400

        daily_data = session.setdefault('daily_data', {})
        current_data = daily_data.setdefault(current_date, {})
        session_entries = current_data.setdefault('entries', {})
        session_entries[tab] = entries
        session.modified = True

        return jsonify({'message': 'Draft saved', 'entries': len(entries)}), 200
    except Exception as e:
        current_app.logger.error(f"Error saving draft: {e}", exc_info=True)
        return jsonify({'error': 'Failed to save draft'}), 500
    
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
                    current_app.logger.debug(f"Failed to save signed work order: {e}")
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
                        current_app.logger.debug(f"Failed to save work order picture: {e}")
                        flash("Failed to save work order picture.", "danger")

            work_orders.append(work_order_entry)
    return work_orders

#def collect_daily_pictures():
    pass

    """
    Collect daily pictures from the Flask request object, save them,
    and return a list of dictionaries with 'Picture' & 'Notes'.
    """
    pictures_of_the_day = []

    # Possibly get a list of files from 'dailyPictures'
    daily_pictures = request.files.getlist('dailyPictures')

    # Retrieve notes from the request form
    daily_picture_notes = request.form.get('dailyPictureNotes', '')

    # Ensure the folder exists
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    for picture in daily_pictures:
        if picture and picture.filename.strip():
            filename = secure_filename(picture.filename)
            picture.save(UPLOAD_FOLDER / filename)
            pictures_of_the_day.append({
                'Picture': filename,
                'Notes': daily_picture_notes
            })

    return pictures_of_the_day
    


#def save_data_to_excel(workers_data=None, materials_data=None, equipment_data=None, subcontractors_data=None, work_orders_data=None, pictures_of_the_day=None, general_notes=None, project_number=None, timestamp=None):
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

        current_app.logger.debug(f"Data appended to Excel file: {file_path}")

    except Exception as e:
        current_app.logger.debug(f"Failed to save data tp excel: {e}")
    