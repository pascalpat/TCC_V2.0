from app import db
from app.models.models import Document
from app.models.core_models import Project, ActivityCode, PaymentItem, CWPackage
from tempfile import TemporaryDirectory
import io
import os
from datetime import datetime

def test_documents_list_empty(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'manager'
    with app.app_context():
        assert Document.query.count() == 0
    response = client.get('/documents/list')
    assert response.status_code == 200
    assert response.get_json()['documents'] == []



def test_download_document(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'manager'
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

def test_upload_document_with_notes(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'manager'
    with app.app_context():
        project = Project(name='TestProj', project_number='TP1', category='Test')
        db.session.add(project)
        db.session.commit()
        project_id = project.id
        tmp_dir = TemporaryDirectory()
        app.config['UPLOAD_FOLDER'] = tmp_dir.name

    data = {
        'project_id': project_id,
        'work_date': datetime.utcnow().isoformat(),
        'document_type': 'general',
        'doc_notes': 'sample note',
        'files': (io.BytesIO(b'content'), 'test.txt'),
    }

    resp = client.post('/documents/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 201

    with client.session_transaction() as sess:
        sess['project_id'] = project_id
        sess['report_date'] = datetime.utcnow().date().isoformat()

    resp = client.get('/documents/list')
    assert resp.status_code == 200
    docs = resp.get_json()['documents']
    assert len(docs) == 1
    assert docs[0]['doc_notes'] == 'sample note'

    tmp_dir.cleanup()


def test_upload_document_with_activity_payment_cwp(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'manager'
    with app.app_context():
        project = Project(name='MixProj', project_number='MX1', category='Test')
        db.session.add(project)
        db.session.commit()
        project_id = project.id

        activity = ActivityCode(code='AC01', description='Desc')
        db.session.add(activity)
        db.session.commit()

        payment = PaymentItem(project_id=project_id, payment_code='PI01',
                              activity_code_id=activity.id, item_name='Item')
        cwp = CWPackage(project_id=project_id, code='CWP1', name='CWP Name')
        db.session.add_all([payment, cwp])
        db.session.commit()

        tmp_dir = TemporaryDirectory()
        app.config['UPLOAD_FOLDER'] = tmp_dir.name

    data = {
        'project_id': project_id,
        'work_date': datetime.utcnow().isoformat(),
        'document_type': 'general',
        'activity_code_id': activity.id,
        'payment_item_id': payment.id,
        'cwp_code': cwp.code,
        'files': (io.BytesIO(b'content2'), 'test2.txt'),
    }

    resp = client.post('/documents/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 201

    with client.session_transaction() as sess:
        sess['project_id'] = project_id
        sess['report_date'] = datetime.utcnow().date().isoformat()

    resp = client.get('/documents/list')
    assert resp.status_code == 200
    docs = resp.get_json()['documents']
    assert len(docs) == 1
    assert docs[0]['activity_code_id'] == activity.id
    assert docs[0]['payment_item_id'] == payment.id
    assert docs[0]['cwp_code'] == cwp.code

    tmp_dir.cleanup()