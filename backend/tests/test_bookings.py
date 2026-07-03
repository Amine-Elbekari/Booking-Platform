import requests
import uuid
from datetime import date, timedelta

# Explicitly define each URL with the required trailing slash for Nginx
USERS_URL = "http://localhost/api/users/"
ASSETS_URL = "http://localhost/api/assets/"
BOOKINGS_URL = "http://localhost/api/bookings/"

def test_booking_engine():
    print("--- 1. Setting up Test Data ---")
    
    random_suffix = str(uuid.uuid4())[:8]
    user_payload = {
        "first_name": "Booking",
        "last_name": "Tester",
        "email": f"booking_{random_suffix}@example.com",
        "phone_number": "+212600000000",
        "date_of_birth": "1990-01-01", 
        "gender": "Male",
        "location": "Casablanca" 
    }
    
    # Use the explicit USERS_URL
    user_res = requests.post(USERS_URL, json=user_payload)
    if user_res.status_code != 201:
        print(f"❌ Failed to create user: {user_res.text}")
        return
    user_id = user_res.json()["id"]
    print(f"✅ User created: {user_id}")

    # Use the explicit ASSETS_URL
    assets_res = requests.get(ASSETS_URL)
    assets = assets_res.json()
    if not assets:
        print("❌ No assets found. Run test_assets.py first.")
        return
    asset_id = assets[0]["id"]
    print(f"✅ Asset retrieved: {asset_id}")

    print("\n--- 2. Testing Raw SQL Booking Transaction ---")
    
    tomorrow = date.today() + timedelta(days=1)
    end_date = tomorrow + timedelta(days=3)

    booking_payload = {
        "user_id": user_id,
        "asset_id": asset_id,
        "start_date": tomorrow.isoformat(),
        "end_date": end_date.isoformat(),
        "adult_count": 2,
        "child_count": 0,
        "baby_count": 0
    }

    # Use the explicit BOOKINGS_URL
    booking_res = requests.post(BOOKINGS_URL, json=booking_payload)
    
    if booking_res.status_code == 201:
        print("✅ SUCCESS: Booking created successfully!")
        print("Response matched BookingResponse model perfectly:")
        print(booking_res.json())
    else:
        print(f"❌ BOOKING FAILED: {booking_res.status_code} - {booking_res.text}")
        return

    print("\n--- 3. Testing Double-Booking Prevention ---")
    
    # Use the explicit BOOKINGS_URL
    conflict_res = requests.post(BOOKINGS_URL, json=booking_payload)
    
    if conflict_res.status_code == 400:
        print("✅ SUCCESS: GiST Engine successfully blocked the double-booking!")
        print(f"Server Response: {conflict_res.json()['detail']}")
    else:
        print(f"❌ FAILED: Engine allowed a double booking or threw wrong error. Status: {conflict_res.status_code}")
        print(conflict_res.text)

if __name__ == "__main__":
    test_booking_engine()