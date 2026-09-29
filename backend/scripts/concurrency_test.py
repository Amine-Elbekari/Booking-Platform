import asyncio
import httpx
import uuid
import sys
import jwt
from datetime import date, timedelta

# Fast concurrency testing script to send 50 requests
# It will login to get a JWT, then send 50 concurrent booking requests.

API_URL = "http://gatekeeper/api"

async def create_user_and_login(client):
    unique_email = f"test_{uuid.uuid4()}@example.com"
    # Create user
    res = await client.post(f"{API_URL}/users/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": unique_email,
        "password": "password123",
        "phone_number": "1234567890",
        "date_of_birth": "1990-01-01",
        "gender": "Male"
    })
    if res.status_code != 201:
        print(f"Failed to create user: {res.text}")
        sys.exit(1)
        
    res = await client.post(f"{API_URL}/auth/login", data={
        "username": unique_email,
        "password": "password123"
    })
    if res.status_code != 200:
        print(f"Failed to login: {res.text}")
        sys.exit(1)
    
    token = res.json()["access_token"]
    payload = jwt.decode(token, options={"verify_signature": False})
    user_id = payload["sub"]
    return token, user_id

async def create_asset(client, token):
    res = await client.post(
        f"{API_URL}/assets/",
        json={
            "name": "Test Villa",
            "asset_type": "Villa",
            "location": "Test Location",
            "price_per_night": 150.0,
            "max_guests": 5
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    if res.status_code != 201:
        print(f"Failed to create asset: {res.text}")
        sys.exit(1)
    
    return res.json()["id"]

async def make_booking_request(client, token, payload):
    try:
        res = await client.post(
            f"{API_URL}/bookings/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.status_code, res.text
    except Exception as e:
        return 500, str(e)

async def main():
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        print("Setting up test data...")
        token, user_id = await create_user_and_login(client)
        asset_id = await create_asset(client, token)
        
        start_date = str(date.today() + timedelta(days=5))
        end_date = str(date.today() + timedelta(days=10))
        
        payload = {
            "asset_id": asset_id,
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
            "adult_count": 2,
            "child_count": 0,
            "baby_count": 0
        }
        
        print(f"Sending 50 concurrent booking requests for Asset ID: {asset_id}...")
        
        # Fire 50 concurrent requests
        tasks = [make_booking_request(client, token, payload) for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        success_count = 0
        conflict_count = 0
        error_count = 0
        
        for status_code, response_data in results:
            if status_code == 201:
                success_count += 1
            elif status_code == 409:
                conflict_count += 1
            else:
                error_count += 1
                print(f"Unexpected error [{status_code}]: {response_data}")
        
        print(f"--- Concurrency Test Results ---")
        print(f"Success (201 Created): {success_count}")
        print(f"Conflicts (409 Conflict): {conflict_count}")
        print(f"Errors: {error_count}")
        
        if success_count == 1 and conflict_count == 49:
            print("SUCCESS! Race condition successfully prevented.")
            sys.exit(0)
        else:
            print("FAILED! The concurrency mechanism did not perform as expected.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
