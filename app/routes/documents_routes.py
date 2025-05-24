from flask import (Blueprint, request, jsonify, session, current_app,url_for, send_from_directory)
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from .. import db
from ..models.models import Document
from ..models.core_models import Project


documents_bp = Blueprint('documents_bp', __name__, url_prefix='/documents')


@documents_bp.route("/files/<path:filename>")
def download_document(filename):
    """Serve a file from the configured upload directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@documents_bp.route("/list", methods=["GET"])
def list_documents():
    """Return documents for the active project and date."""
    proj_val = session.get("project_id")
    report_date = session.get("report_date")

    if not proj_val or not report_date:
        return jsonify(documents=[]), 200

    # Resolve numeric project.id
    project = None
    if isinstance(proj_val, str) and not proj_val.isdigit():
        project = Project.query.filter_by(project_number=proj_val).first()
    else:
        try:
            project = Project.query.get(int(proj_val))
        except (TypeError, ValueError):
            pass
    if not project:
        return jsonify(documents=[]), 200

    try:
        date_obj = datetime.fromisoformat(report_date).date()
    except ValueError:
        date_obj = None

    query = Document.query.filter_by(project_id=project.id)
    if date_obj:
        start = datetime.combine(date_obj, datetime.min.time())
        end = datetime.combine(date_obj, datetime.max.time())
    query = query.filter(Document.uploaded_at >= start, Document.uploaded_at <= end)
    query = query.filter(Document.status.in_(["pending", "committed"]))


    docs = query.all()

    results = [
        {
            "id": d.id,
            "file_name": d.file_name,
            "file_url": url_for("documents_bp.download_document", filename=os.path.basename(d.file_url)),
            "document_type": d.document_type,
            "status": d.status,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        }
        for d in docs
    ]
    return jsonify(documents=results), 200


@documents_bp.route("/upload", methods=["POST"])

def upload_documents():
    """Upload one or more files and create pending Document records."""

    proj_val = session.get("project_id") or request.form.get("project_id")
    work_date = session.get("report_date") or request.form.get("work_date")
    doc_type = request.form.get("document_type", "general")
    files = request.files.getlist("files")

    if not proj_val or not files:
        return jsonify(error="project_id and files are required"), 400


    # resolve project
    project = None
    if isinstance(proj_val, str) and not proj_val.isdigit():
        project = Project.query.filter_by(project_number=proj_val).first()
    else:
        try:
            project = Project.query.get(int(proj_val))
        except (TypeError, ValueError):
            pass
    if not project:
        return jsonify(error="Invalid project"), 400

    try:
        upload_dt = datetime.fromisoformat(work_date)
    except Exception:
        upload_dt = datetime.utcnow()

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

    os.makedirs(upload_folder, exist_ok=True)

    created = []
    saved_paths = []
    try:
        for f in files:
            if not f or not f.filename:
                continue
            filename = secure_filename(f.filename)
            save_path = os.path.join(upload_folder, filename)
            f.save(save_path)
            saved_paths.append(save_path)
            rel_path = os.path.relpath(save_path, start=current_app.root_path)

            doc = Document(
                project_id=project.id,
                file_name=filename,
                file_url=rel_path,
                uploaded_at=upload_dt,
                document_type=doc_type,
                status="pending"
                )
            db.session.add(doc)
            created.append(doc)

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        for path in saved_paths:
            try:
                os.remove(path)
            except OSError:
                pass
        current_app.logger.exception(exc)
        return jsonify(error='Upload failed'), 500
    return jsonify(records=[d.id for d in created]), 201
