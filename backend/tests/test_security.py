# backend/test_security.py
import requests
import uuid
from datetime import date, timedelta
import random

API_URL = "http://localhost/api"

def test_security_flow():
    print("--- 1. Registering a New User ---")
    random_suffix = str(uuid.uuid4())[:8]
    email = f"secure_{random_suffix}@example.com"
    password = "SuperSecretPassword123!"
    
    user_payload = {
        "first_name": "Secure",
        "last_name": "Tester",
        "email": email,
        "password": password, 
        "phone_number": "+212600000000",
        "date_of_birth": "1990-01-01", 
        "gender": "Male",
        "location": "Casablanca"
    }
    
    user_res = requests.post(f"{API_URL}/users/", json=user_payload)
    if user_res.status_code != 201:
        print(f"❌ Failed to create user: {user_res.text}")
        return
    user_id = user_res.json()["id"]
    print(f"✅ User registered successfully. ID: {user_id}")

    print("\n--- 2. Logging In to get JWT ---")
    # OAuth2 expects form-encoded data, not JSON
    login_data = {
        "username": email,
        "password": password
    }
    login_res = requests.post(f"{API_URL}/auth/login", data=login_data)
    
    if login_res.status_code != 200:
        print(f"❌ Login failed: {login_res.text}")
        return
    
    token = login_res.json()["access_token"]
    print(f"✅ Login successful! JWT generated:\n{token[:50]}...[TRUNCATED]")

    # Setup booking payload
    assets_res = requests.get(f"{API_URL}/assets/")
    asset_id = assets_res.json()[0]["id"]
    tomorrow = date.today() + timedelta(days=5)
    end_date = tomorrow + timedelta(days=2)
    
    random_offset = random.randint(10, 100) 
    start_booking = date.today() + timedelta(days=random_offset)
    end_booking = start_booking + timedelta(days=3)
    
    booking_payload = {
        "user_id": user_id,
        "asset_id": asset_id,
        "start_date": start_booking.isoformat(),
        "end_date": end_booking.isoformat(),
        "adult_count": 2,
        "child_count": 0,
        "baby_count": 0
    }

    print("\n--- 3. ATTACK: Booking with NO Token ---")
    attack_1 = requests.post(f"{API_URL}/bookings/", json=booking_payload)
    if attack_1.status_code == 401:
        print("✅ SUCCESS: Server blocked request with NO token (401 Unauthorized)")
    else:
        print(f"❌ FAILED: Server allowed access! Status: {attack_1.status_code}")

    print("\n--- 4. ATTACK: Booking with FAKE Token ---")
    headers_fake = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake_payload.fake_signature"}
    attack_2 = requests.post(f"{API_URL}/bookings/", json=booking_payload, headers=headers_fake)
    if attack_2.status_code == 401:
        print("✅ SUCCESS: Server blocked request with FAKE token (401 Unauthorized)")
    else:
        print(f"❌ FAILED: Server allowed access! Status: {attack_2.status_code}")

    print("\n--- 5. LEGITIMATE: Booking with REAL Token ---")
    headers_real = {"Authorization": f"Bearer {token}"}
    legit_res = requests.post(f"{API_URL}/bookings/", json=booking_payload, headers=headers_real)
    
    if legit_res.status_code == 201:
        print("✅ SUCCESS: Booking created using valid JWT!")
        print(legit_res.json())
    else:
        print(f"❌ FAILED: Legitimate booking rejected. Status: {legit_res.status_code} - {legit_res.text}")

if __name__ == "__main__":
    test_security_flow()