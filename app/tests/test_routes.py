"""Basic route tests"""

from werkzeug.security import generate_password_hash
from app import db
from app.models.workforce_models import Worker

def test_redirect_to_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')


def test_calendar_requires_login(client):
    resp = client.get('/calendar/')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')

def test_login_with_email(client, app):
    with app.app_context():
        worker = Worker(
            name='Test User',
            worker_id='T123',
            courriel='user@example.com',
            password_hash=generate_password_hash('secret'),
            role='manager',
        )
        db.session.add(worker)
        db.session.commit()

    resp = client.post('/auth/login', data={'email': 'user@example.com', 'password': 'secret'})
    assert resp.status_code == 302
    assert '/projects' in resp.headers.get('Location', '')
    with client.session_transaction() as sess:
        assert sess['user_id'] == worker.id
        assert sess['role'] == 'manager'
    
def test_admin_requires_admin_role(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'worker'
    resp = client.get('/admin/')
    assert resp.status_code == 403


def test_master_table_requires_manager(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'worker'
    resp = client.get('/projects/list')
    assert resp.status_code == 403