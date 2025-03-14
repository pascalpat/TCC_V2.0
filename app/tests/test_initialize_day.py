import requests

def test_initialize_day():
    """Test the /initialize-day endpoint."""
    url = "http://127.0.0.1:5001/data-entry/initialize-day"
    data = {"dateStamp": "2024-12-06"}
    
    try:
        # Make the POST request to initialize the day
        response = requests.post(url, json=data)

        # Output the status code and response
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())

        # Validate the response
        if response.status_code == 200 and response.json().get("status") == "success":
            print("Test Passed: Date initialized successfully!")
        else:
            print("Test Failed:", response.json().get("message", "Unknown Error"))
    except Exception as e:
        print("Error during test:", str(e))

if __name__ == "__main__":
    test_initialize_day()
