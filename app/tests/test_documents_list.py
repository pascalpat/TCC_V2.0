import pytest
from app import create_app, db
from app.models.models import Document
from app.models.core_models import Project
import os
from datetime import datetime

def test_documents_list_empty():
    app = create_app('testing')
    app.testing = True
    with app.app_context():
        db.create_all()
        assert Document.query.count() == 0
        client = app.test_client()
        response = client.get('/documents/list')
        assert response.status_code == 200
        assert response.get_json()['documents'] == []
        db.session.remove()
        db.drop_all()


def test_download_document(client, app):
    with app.app_context():
        project = Project(name='P', project_number='P1', category='Test')
        db.session.add(project)
        db.session.commit()
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filename = 'sample.txt'
        content = b'Hello world'
        file_path = os.path.join(upload_folder, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        rel_path = os.path.relpath(file_path, start=app.root_path)
        doc = Document(project_id=project.id, file_name=filename, file_url=rel_path,
                       document_type='general', status='pending', uploaded_at=datetime.utcnow())
        db.session.add(doc)
        db.session.commit()

    response = client.get(f'/documents/files/{filename}')
    assert response.status_code == 200
    assert response.data == content

    os.remove(file_path)