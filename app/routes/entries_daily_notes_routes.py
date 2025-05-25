# app/routes/entries_daily_notes_routes.py

from flask import Blueprint, jsonify, session, current_app, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from ..models.daily_models import DailyNoteEntry
from ..models.core_models import Project
from .. import db
from datetime import datetime, date

entries_daily_notes_bp = Blueprint('entries_daily_notes_bp', __name__, url_prefix='/entries_daily_notes')

@entries_daily_notes_bp.route('/list', methods=['GET'])
def get_daily_notes():
    """
    Return JSON of all DailyNoteEntry rows for the currently
    selected project & report date (from session).
    Front-end expects: { entries: [ {…}, {…}, … ] }
    """
    try:
        # 1) Base query
        q = DailyNoteEntry.query

        # 2) Filter by project if in session
        proj_id = session.get('project_id')
        if proj_id:
            q = q.filter_by(project_id=proj_id)

        # 3) Filter by report_date if in session
        report_date = session.get('report_date')
        if report_date:
            # Accept ISO string or date object
            if isinstance(report_date, str):
                try:
                    report_date = datetime.fromisoformat(report_date).date()
                except ValueError:
                    current_app.logger.debug(
                        f"Invalid report_date format: {report_date}")
                    report_date = None
            elif isinstance(report_date, datetime):
                report_date = report_date.date()
            elif not isinstance(report_date, date):
                current_app.logger.debug(
                    f"Unsupported report_date type: {type(report_date)}")
                report_date = None

        current_app.logger.debug(
            "get_daily_notes session values: project_id=%s, report_date=%s",
            proj_id, report_date)

        if report_date:
            q = q.filter(DailyNoteEntry.date_of_report == report_date)


        # 4) Optional: order chronologically
        q = q.order_by(DailyNoteEntry.note_datetime.asc())

        # 5) Execute & serialize
        notes = q.all()
        entries = [note.to_dict() for note in notes]

        # 6) Return exactly what your JS is looking for
        return jsonify(entries=entries), 200

    except SQLAlchemyError as e:
        current_app.logger.debug(
            "Exception in get_daily_notes", exc_info=True
        )
        current_app.logger.debug(
            "Session state on error: project_id=%s, report_date=%s",
            proj_id, session.get('report_date')
        )
        return jsonify(error="Database error fetching daily notes"), 500

@entries_daily_notes_bp.route('/', methods=['POST'])
def add_daily_note():
    """Create a new daily note entry, saving a numeric project_id & a date_of_report."""
    data = request.get_json(silent=True) or {}

    # 1) Grab the raw project identifier
    proj_val = session.get('project_id') or data.get('project_id')
    if not proj_val:
        return jsonify(error="No active project selected"), 400

    # 1a) Turn it into the true numeric projects.id
    if isinstance(proj_val, str):
        # digits? cast directly
        if proj_val.isdigit():
            project_id = int(proj_val)
        else:
            # otherwise treat it as a project_number → look it up
            proj_obj = Project.query.filter_by(project_number=proj_val).first()
            if not proj_obj:
                return jsonify(error=f"Project '{proj_val}' not found"), 400
            project_id = proj_obj.id
    else:
        # not a string? hope it’s already an int or convertible
        try:
            project_id = int(proj_val)
        except (TypeError, ValueError):
            return jsonify(error="Invalid project_id"), 400

    # 2) Compute date_of_report (session date → payload → today)
    session_date = session.get('report_date')  # "YYYY-MM-DD"
    if session_date:
        try:
            report_date = date.fromisoformat(session_date)
        except ValueError:
            report_date = datetime.utcnow().date()
    else:
        dt_str = data.get('note_datetime')
        if dt_str:
            try:
                report_date = datetime.fromisoformat(dt_str).date()
            except ValueError:
                report_date = datetime.utcnow().date()
        else:
            report_date = datetime.utcnow().date()

    # 3) Parse note_datetime override or use now
    nd = data.get('note_datetime')
    if nd:
        try:
            note_datetime = datetime.fromisoformat(nd)
        except ValueError:
            note_datetime = datetime.utcnow()
    else:
        note_datetime = datetime.utcnow()

    # 4) Ensure required content
    content = (data.get('content') or "").strip()
    if not content:
        return jsonify(error="Content is required"), 400

    # 5) Instantiate and stage the new note
    new_note = DailyNoteEntry(
        project_id       = project_id,
        note_datetime    = note_datetime,
        date_of_report   = report_date,
        author           = data.get('author'),
        category         = data.get('category'),
        tags             = data.get('tags'),
        content          = content,
        priority         = data.get('priority', 'low'),
        status           = data.get('status'),  # or omit to use default
        activity_code_id = data.get('activity_code_id'),
        payment_item_id  = data.get('payment_item_id'),
        work_order_id    = data.get('work_order_id'),
        cwp              = data.get('cwp'),
        editable_by      = data.get('editable_by'),
    )
    db.session.add(new_note)

    # 6) Commit or rollback
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error("DB error adding daily note: %s", e, exc_info=True)
        return jsonify(error="Database error adding daily note"), 500

    # 7) Return the freshly‐created note
    return jsonify(note=new_note.to_dict()), 201


@entries_daily_notes_bp.route('/<int:note_id>', methods=['GET'])
def get_daily_note(note_id: int):
    """Retrieve a single daily note by its ID."""
    try:
        note = DailyNoteEntry.query.get(note_id)
        if not note:
            return jsonify({"error": "Daily note not found"}), 404
        return jsonify(note.to_dict()), 200
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error fetching daily note {note_id}: {e}", exc_info=True)
        return jsonify({"error": "Database error fetching daily note"}), 500

@entries_daily_notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_daily_note(note_id: int):
    """Update an existing daily note."""
    data = request.get_json() or {}
    if 'content' in data and not data['content']:
        return jsonify({"error": "content cannot be empty"}), 400

    try:
        note = DailyNoteEntry.query.get(note_id)
        if not note:
            return jsonify({"error": "Daily note not found"}), 404

        note_dt = data.get('note_datetime')
        if note_dt is not None:
            note.note_datetime = datetime.fromisoformat(note_dt) if note_dt else None

        if 'activity_code_id' in data:
            act_val = data['activity_code_id']
            note.activity_code_id = (
                int(act_val) if act_val not in (None, "") else None
            )

        if 'payment_item_id' in data:
            pay_val = data['payment_item_id']
            note.payment_item_id = (
                int(pay_val) if pay_val not in (None, "") else None
            )

            
        if 'work_order_id' in data:
            wo_val = data['work_order_id']
            note.work_order_id = (
                int(wo_val) if wo_val not in (None, "") else None
            )



        for field in [
            'project_id',
            'author',
            'category',
            'tags',
            'content',
            'priority',
            'cwp',
            'editable_by',
        ]:
            if field in data:
                setattr(note, field, data[field])

        db.session.commit()
        return jsonify(note.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error updating daily note {note_id}: {e}", exc_info=True)
        return jsonify({"error": "Database error updating daily note"}), 500


@entries_daily_notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_daily_note(note_id: int):
    """Delete a daily note from the database."""
    try:
        note = DailyNoteEntry.query.get(note_id)
        if not note:
            return jsonify({"error": "Daily note not found"}), 404
        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "Daily note deleted"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting daily note {note_id}: {e}", exc_info=True)
        return jsonify({"error": "Database error deleting daily note"}), 500
    
@entries_daily_notes_bp.route('/confirm', methods=['POST'])
def confirm_daily_notes():
    """Bulk create daily notes from staged entries."""
    data = request.get_json() or {}
    notes = data.get('notes')
    if not notes or not isinstance(notes, list):
        return jsonify(error="Missing notes list"), 400

    created = []
    try:
        for n in notes:
            if not n.get('project_id') or not n.get('content'):
                return jsonify(error="project_id and content are required"), 400

            note_dt = n.get('note_datetime')
            note_datetime = datetime.fromisoformat(note_dt) if note_dt else None
            date_of_report = note_datetime.date() if note_datetime else datetime.utcnow().date()

            try:
                act_id = int(n['activity_code_id']) if n.get('activity_code_id') else None
            except (TypeError, ValueError):
                return jsonify(error="Invalid activity_code_id"), 400

            try:
                pay_id = int(n['payment_item_id']) if n.get('payment_item_id') else None
            except (TypeError, ValueError):
                return jsonify(error="Invalid payment_item_id"), 400

            try:
                wo_id = int(n['work_order_id']) if n.get('work_order_id') else None
            except (TypeError, ValueError):
                return jsonify(error="Invalid work_order_id"), 400
            
            new_note = DailyNoteEntry(
                project_id=n.get('project_id'),
                note_datetime=note_datetime,
                date_of_report=date_of_report,
                author=n.get('author'),
                category=n.get('category'),
                tags=n.get('tags'),
                content=n.get('content'),
                priority=n.get('priority'),
                activity_code_id=act_id,
                payment_item_id=pay_id,
                work_order_id=wo_id,
                cwp=n.get('cwp'),
                editable_by=n.get('editable_by'),
            )
            db.session.add(new_note)
            created.append(new_note)

        db.session.commit()
        return jsonify(records=[c.id for c in created]), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error confirming notes: {e}", exc_info=True)
        return jsonify(error="Database error confirming notes"), 500
