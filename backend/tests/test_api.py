# backend/test_api.py
import requests
import uuid

API_URL = "http://localhost/api/users/"

def test_create_and_get_user():
    print("--- 1. Testing POST /api/users/ ---")
    
    # Generate a random 8 character string to make the email unique
    random_suffix = str(uuid.uuid4())[:8]
    
    payload = {
        "first_name": "API",
        "last_name": "Tester",
        "email": f"apitest_{random_suffix}@example.com",
        "phone_number": "+212611111111",
        "date_of_birth": "1995-05-05", 
        "gender": "Female",
        "address": "Casablanca Center",
        "country": "Morocco",
        "city": "Casablanca"
    }
    
    # Step 1: Create the user
    post_response = requests.post(API_URL, json=payload)
    
    if post_response.status_code == 201:
        user_data = post_response.json()
        user_id = user_data["id"]
        print(f"✅ SUCCESS: User created with ID: {user_id}")
        
        # Step 2: Test the GET endpoint using the ID we just received
        print(f"\n--- 2. Testing GET /api/users/{user_id} ---")
        get_url = f"http://localhost/api/users/{user_id}"
        
        get_response = requests.get(get_url)
        
        if get_response.status_code == 200:
            print("✅ SUCCESS: User retrieved successfully from the database!")
            print("Retrieved Data:")
            print(get_response.json())
        else:
            print(f"❌ GET ERROR {get_response.status_code}: {get_response.text}")
            
    else:
        print(f"❌ CRITICAL POST ERROR {post_response.status_code}: {post_response.text}")

if __name__ == "__main__":
    test_create_and_get_user()