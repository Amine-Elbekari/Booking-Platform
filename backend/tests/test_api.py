import sys
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import uuid
import random
from datetime import date, timedelta

# 1. Calculate our current directory structure
current_file_path = os.path.abspath(__file__)
tests_dir = os.path.dirname(current_file_path)
backend_dir = os.path.dirname(tests_dir)

# 2. Go up ONE MORE LEVEL to the root directory where docker-compose lives
root_dir = os.path.dirname(backend_dir) 

# 3. Load the .env from the ROOT directory
load_dotenv(os.path.join(root_dir, '.env'))

# 4. Inject the backend/ directory into Python's path
sys.path.append(backend_dir)

# 5. Now import the app!
from main import app  

# Create the test client


def test_full_user_and_booking_lifecycle():
    """
    Tests the entire flow: Registration -> Login -> Fetch Asset -> Booking -> Double Booking Block
    """
    with TestClient(app) as client:
        # --- 1. REGISTRATION ---
        random_suffix = str(uuid.uuid4())[:8]
        email = f"pytest_{random_suffix}@example.com"
        password = "SuperSecretPassword123!"

        user_payload = {
            "first_name": "Pytest",
            "last_name": "Runner",
            "email": email,
            "password": password,
            "phone_number": "+212600000000",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "location": "Casablanca"
        }

        reg_response = client.post("/users/", json=user_payload)
        assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"
        user_id = reg_response.json()["id"]

        # --- 2. LOGIN & JWT GENERATION ---
        login_data = {"username": email, "password": password}
        login_response = client.post("/auth/login", data=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # --- 3. FETCH ASSETS ---
        assets_response = client.get("/assets/")
        assert assets_response.status_code == 200
        assets = assets_response.json()
        assert len(assets) > 0, "No assets found in the database. Run your asset seeder."
        asset_id = assets[0]["id"]

        # --- 4. SUCCESSFUL BOOKING ---
        # Use random future dates to prevent collision with previous test runs
        random_offset = random.randint(100, 500)
        start_date = date.today() + timedelta(days=random_offset)
        end_date = start_date + timedelta(days=3)

        booking_payload = {
            "user_id": user_id,
            "asset_id": asset_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "adult_count": 2,
            "child_count": 0,
            "baby_count": 0
        }

        booking_response = client.post("/bookings/", json=booking_payload, headers=headers)
        assert booking_response.status_code == 201, f"Booking failed: {booking_response.text}"

        # --- 5. DOUBLE BOOKING CONSTRAINT (GiST) ---
        conflict_response = client.post("/bookings/", json=booking_payload, headers=headers)
        assert conflict_response.status_code == 400
        assert "already booked" in conflict_response.json()["detail"]