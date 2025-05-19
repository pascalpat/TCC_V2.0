from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from ..models.daily_models import DailyNoteEntry
from .. import db


# Define the Blueprint for daily notes
dailynotes_bp = Blueprint('dailynotes_bp', __name__, url_prefix='/dailynotes')


@dailynotes_bp.route('/list', methods=['GET'])
def get_daily_notes():
    """Return all daily notes stored in the database."""
    try:
        notes = DailyNoteEntry.query.all()
        return jsonify({"daily_notes": [n.to_dict() for n in notes]}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error fetching daily notes: {e}", exc_info=True)
        return jsonify({"error": "Database error fetching daily notes"}), 500

@dailynotes_bp.route('/', methods=['POST'])
def add_daily_note():
    """Create a new daily note entry in the database."""
    data = request.get_json() or {}

    if not data.get('project_id') or not data.get('content'):
        return jsonify({"error": "project_id and content are required"}), 400

    try:
        note_dt = data.get('note_datetime')
        note_datetime = datetime.fromisoformat(note_dt) if note_dt else None

        new_note = DailyNoteEntry(
            project_id=data.get('project_id'),
            note_datetime=note_datetime,
            author=data.get('author'),
            category=data.get('category'),
            tags=data.get('tags'),
            content=data.get('content'),
            priority=data.get('priority'),
            activity_code_id=data.get('activity_code_id'),
            payment_item_id=data.get('payment_item_id'),
            cwp=data.get('cwp'),
            editable_by=data.get('editable_by'),
        )

        db.session.add(new_note)
        db.session.commit()
        return jsonify(new_note.to_dict()), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error adding daily note: {e}", exc_info=True)
        return jsonify({"error": "Database error adding daily note"}), 500


@dailynotes_bp.route('/<int:note_id>', methods=['GET'])
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

@dailynotes_bp.route('/<int:note_id>', methods=['PUT'])
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

        for field in [
            'project_id',
            'author',
            'category',
            'tags',
            'content',
            'priority',
            'activity_code_id',
            'payment_item_id',
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


@dailynotes_bp.route('/<int:note_id>', methods=['DELETE'])
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
