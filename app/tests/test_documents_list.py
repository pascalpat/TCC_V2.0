import pytest
from app import create_app, db
from app.models.models import Document


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