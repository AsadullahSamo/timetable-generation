import requests
import json

# Test the shared access endpoint
def test_shared_access():
    base_url = "http://localhost:8000"
    
    # Test data (you'll need to adjust these IDs based on your database)
    test_data = {
        "shared_with": 2,  # Replace with actual user ID
        "department": 1,   # Replace with actual department ID
        "access_level": "VIEW",
        "notes": "Test shared access",
        "share_subjects": True,
        "share_teachers": True,
        "share_classrooms": True,
        "share_batches": True,
        "share_constraints": True,
        "share_timetable": True
    }
    
    try:
        # Test POST request
        response = requests.post(
            f"{base_url}/api/timetable/shared-access/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Shared access created successfully!")
        else:
            print("❌ Failed to create shared access")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_shared_access()
