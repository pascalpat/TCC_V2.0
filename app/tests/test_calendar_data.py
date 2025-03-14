import json

from flask import session
import sys
print("Python Path:", sys.path)
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app  # Ensure this imports your Flask app factory

def test_calendar_data():
    # Create the app and test client
    app = create_app()
    app.testing = True  # Enable testing mode
    client = app.test_client()

    # Mock user session data
    
    with client.session_transaction() as session:
        session['user_id'] = '101'  # Example user ID
        session['daily_data'] = {
            "2024-12-10": {
                "projects": {
                    "24-401": {"status": "completed"},
                    "24-404": {"status": "not_started"}
                }
            },
            "2024-12-09": {
                "projects": {
                    "24-401": {"status": "in_progress"}
                }
            }
        }

    # Call the /calendar-data route
    response = client.get('/calendar/calendar-data')

    # Verify the response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = json.loads(response.data)

    # Print the result for debugging
    print("Response JSON:")
    print(json.dumps(data, indent=4))

    # Example assertions to validate the response structure
    assert 'calendar' in data, "Response should contain 'calendar' key"
    assert "2024-12-10" in data['calendar'], "Date '2024-12-10' should be in calendar"
    assert "24-401" in data['calendar']["2024-12-10"], "Project '24-401' should be listed under '2024-12-10'"
    assert data['calendar']["2024-12-10"]["24-401"] == "completed", "Status of project '24-401' should be 'completed'"

    print("Test passed!")

if __name__ == "__main__":
    test_calendar_data()
