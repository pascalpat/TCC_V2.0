from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from .. import db
from ..models import Document, DailyPicture
import pandas as pd

media_bp = Blueprint('media_bp', __name__, url_prefix='/media')

def load_data(filepath, columns=None):
    """Load data from a CSV file using pandas."""
    df = pd.read_csv(filepath)
    if columns:
        df = df[columns]
    return df

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def _is_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

@media_bp.route('/upload', methods=['POST'])
def upload_media():
    """Upload files and create Document or DailyPicture records."""
    project_id = request.form.get('project_id')
    work_date = request.form.get('work_date')
    activity_code = request.form.get('activity_code')
    category = request.form.get('category')
    files = request.files.getlist('files')

    if not project_id or not files:
        return jsonify({'error': 'project_id and files are required'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    os.makedirs(upload_folder, exist_ok=True)

    created = []
    for file in files:
        if not file or not file.filename:
            continue
        filename = secure_filename(file.filename)
        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)
        rel_path = os.path.relpath(save_path, start=current_app.root_path)

        if _is_image(filename):
            record = DailyPicture(
                project_id=project_id,
                file_name=filename,
                file_url=rel_path,
                uploaded_at=datetime.utcnow(),
                activity_code=activity_code,
                description=category,
                status='pending'
            )
            db.session.add(record)
            created.append({'type': 'picture', 'file': filename})
        else:
            record = Document(
                project_id=project_id,
                file_name=filename,
                file_url=rel_path,
                uploaded_at=datetime.utcnow(),
                document_type=category or 'general',
                category=category,
                status='pending'
            )
            db.session.add(record)
            created.append({'type': 'document', 'file': filename})
    db.session.commit()
    return jsonify({'message': 'Files uploaded successfully', 'created': created}), 201

@media_bp.route('/media/list', methods=['GET'])
def list_media():
    """Return pictures and document records."""
    pics_file = current_app.config.get('DAILY_PICTURES_FILE')
    docs_file = current_app.config.get('DOCUMENTS_FILE')

    media = []
    if pics_file and os.path.exists(pics_file):
        df = load_data(pics_file, columns=['file_name', 'description', 'file_url'])
        media += [
            {
                'filename': row.get('file_name'),
                'description': row.get('description', ''),
                'url': row.get('file_url'),
                'type': 'picture',
                'status': 'committed'
            }
            for _, row in df.iterrows()
        ]

    if docs_file and os.path.exists(docs_file):
        df = load_data(docs_file, columns=['file_name', 'file_url', 'document_type'])
        media += [
            {
                'filename': row.get('file_name'),
                'description': '',
                'url': row.get('file_url'),
                'type': 'pdf' if str(row.get('document_type', '')).lower().endswith('pdf') else 'document',
                'status': 'committed'
            }
            for _, row in df.iterrows()
        ]

    return jsonify({'media': media})


@media_bp.route('/confirm', methods=['POST'])
def confirm_media():
    """Placeholder endpoint to accept staged media."""
    data = request.get_json() or {}
    media_list = data.get('media', [])
    return jsonify(records=list(range(len(media_list)))), 200