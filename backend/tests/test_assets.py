# backend/test_assets.py
import requests

API_URL = "http://localhost/api/assets/"

def populate_assets():
    print("--- 1. Populating Assets ---")
    
    assets_to_create = [
        {
            "name": "Luxury Oceanfront Villa",
            "asset_type": "Villa",
            "location": "Tangier",
            "price_per_night": 350.00,
            "max_guests": 8
        },
        {
            "name": "Traditional Riad Majorelle",
            "asset_type": "Riad",
            "location": "Marrakech",
            "price_per_night": 120.00,
            "max_guests": 4
        },
        {
            "name": "Downtown Twin Center Apartment",
            "asset_type": "Apartment",
            "location": "Casablanca",
            "price_per_night": 85.00,
            "max_guests": 2
        }
    ]
    
    for asset in assets_to_create:
        response = requests.post(API_URL, json=asset)
        if response.status_code == 201:
            print(f"✅ Created: {asset['name']}")
        else:
            print(f"❌ Failed to create {asset['name']}: {response.text}")

    print("\n--- 2. Fetching All Assets ---")
    get_response = requests.get(API_URL)
    
    if get_response.status_code == 200:
        all_assets = get_response.json()
        print(f"✅ Successfully retrieved {len(all_assets)} assets from the database!")
    else:
        print(f"❌ Failed to fetch assets: {get_response.text}")

if __name__ == "__main__":
    populate_assets()