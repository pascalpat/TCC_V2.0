# app/routes/dailynotes_routes.py

import os
from uuid import uuid4
from datetime import datetime

from flask import (
    Blueprint, request, jsonify,
    current_app, url_for, abort, session
)
from werkzeug.utils import secure_filename

from app.models.daily_models import DailyNote, db

dailynotes_bp = Blueprint(
    'dailynotes',
    __name__,
    url_prefix='/daily_notes'
)

def save_attachment(file):
    """Save upload under static/uploads and return its URL path."""
    fn = f"{uuid4().hex}_{secure_filename(file.filename)}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    full_path = os.path.join(upload_folder, fn)
    file.save(full_path)
    return url_for('static', filename=f'uploads/{fn}', _external=False)


@dailynotes_bp.route('/get-speech-config', methods=['GET'])
def get_speech_config():
    """
    Return the Azure Speech subscription key and region
    (so the front-end can initialize SpeechSDK).
    """
    key    = current_app.config.get('AZURE_SPEECH_KEY')
    region = current_app.config.get('AZURE_SPEECH_REGION')

    if not key or not region:
        return jsonify({'error': 'Speech config not set'}), 500

    return jsonify({
        'apiKey': key,
        'region': region
    })


@dailynotes_bp.route('/list', methods=['GET'])
def list_notes():
    """Return the most recent 50 notes as JSON."""
    notes = (
        DailyNote.query
                 .order_by(DailyNote.created_at.desc())
                 .limit(50)
                 .all()
    )
    return jsonify([{
        'id': str(n.id),
        'content': n.content,
        'category': n.category,
        'priority': n.priority,
        'work_order_id': n.work_order_id,
        'attachment_url': n.attachment_url,
        'created_by': n.created_by,
        'created_at': n.created_at.isoformat()
    } for n in notes])


@dailynotes_bp.route('/add', methods=['POST'])
def add_note():
    """
    Accepts multipart/form-data:
      - content       (required)
      - category      (optional)
      - priority      (optional, defaults to 'low')
      - work_order_id (optional)
      - attachment    (optional file)
    Persists a DailyNote and returns {status, id}.
    """
    form = request.form
    content = form.get('content', '').strip()
    if not content:
        return jsonify({'error': 'content is required'}), 400

    category = form.get('category')
    priority = form.get('priority', 'low')
    wo_id    = form.get('work_order_id') or None

    # Handle file
    attachment_url = None
    file = request.files.get('attachment')
    if file and file.filename:
        attachment_url = save_attachment(file)

    note = DailyNote(
        content        = content,
        category       = category,
        priority       = priority,
        work_order_id  = wo_id,
        attachment_url = attachment_url,
        created_by     = session.get('user', 'anonymous')
    )

    db.session.add(note)
    db.session.commit()

    return jsonify({'status': 'ok', 'id': str(note.id)}), 201


@dailynotes_bp.route('/<note_id>', methods=['PATCH'])
def update_note(note_id):
    """
    Update fields of an existing note.
    Accepts multipart/form-data or JSON:
      - content       (optional)
      - category      (optional)
      - priority      (optional)
      - work_order_id (optional)
      - attachment    (optional file to replace existing)
    """
    note = DailyNote.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # accept both JSON and form-data
    data = request.form if request.form else request.get_json() or {}

    # Update text fields if provided
    if 'content' in data:
        note.content = data.get('content', note.content).strip()
    if 'category' in data:
        note.category = data.get('category')
    if 'priority' in data:
        note.priority = data.get('priority')
    if 'work_order_id' in data:
        note.work_order_id = data.get('work_order_id') or None

    # Handle file replacement if provided
    file = request.files.get('attachment')
    if file and file.filename:
        note.attachment_url = save_attachment(file)

    note.updated_at = datetime.utcnow()  # if you have such a column
    db.session.commit()

    return jsonify({'status': 'ok'}), 200


@dailynotes_bp.route('/commit', methods=['POST'])
def commit_notes():
    # …your existing logic to persist & clear session…
    return '', 204


@dailynotes_bp.route('/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a persisted note by its UUID."""
    note = DailyNote.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    db.session.delete(note)
    db.session.commit()
    return '', 204
