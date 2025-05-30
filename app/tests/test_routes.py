"""Basic route tests"""

from app import app

def test_redirect_to_login():
	with app.test_client() as client:
		response = client.get('/')  # Replace '/' with the route you want to test
		assert response.status_code == 302
		assert '/login' in response.headers.get('Location', '')
