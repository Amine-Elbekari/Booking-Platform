"""
Agentic Layer Test Suite
Run: docker compose exec api python scripts/agent_test.py
"""
import httpx
import time
import uuid

API = "http://localhost:8000"
TIMEOUT = httpx.Timeout(120.0)

def sep(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    time.sleep(2) # Give Ollama breathing room

def generate_pdf(content_text):
    return f"""%PDF-1.4
1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj
2 0 obj<</Type /Pages /Kids[3 0 R] /Count 1>>endobj
3 0 obj<</Type /Page /Parent 2 0 R /MediaBox[0 0 612 792] /Contents 4 0 R /Resources<</Font<</F1<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>>>>>  >>endobj
4 0 obj<</Length {len(content_text) + 50}>>stream
BT /F1 11 Tf 50 750 Td
({content_text}) Tj
ET
endstream endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000313 00000 n
trailer<</Size 5 /Root 1 0 R>>
startxref
760
%%EOF""".encode('utf-8')

VILLA_POLICY = generate_pdf("Cancel free 48h before checkin. Paid in full. Checkin 3 PM, late after 8 PM needs notice. Max 4 guests, extra incurs fee.")
UNRELATED_PDF = generate_pdf("This document is about the culinary history of ancient Rome and their use of garum.")

def wait_for_ready(client, auth, doc_id, timeout=20):
    for _ in range(timeout):
        time.sleep(1.5)
        docs = client.get("/rag/documents", headers=auth).json()
        doc = next((d for d in docs if d["id"] == doc_id), None)
        if doc and doc["status"] == "READY":
            return True
        if doc and doc["status"] == "FAILED":
            print(f"Document {doc_id} failed ingestion!")
            return False
    print("Timeout waiting for document ingestion.")
    return False

def main():
    with httpx.Client(base_url=API, timeout=TIMEOUT, follow_redirects=True) as client:
        # Check Health
        r = client.get("/rag/health")
        print("Health check:", r.json())
        
        # Create User A
        email_a = f"usera_{uuid.uuid4().hex[:6]}@test.com"
        client.post("/users/", json={"first_name": "TestA", "last_name": "UserA", "email": email_a, "password": "Password123!", "phone_number": "000000", "date_of_birth": "1990-01-01", "gender": "Male", "location": "Morocco"})
        token_a = client.post("/auth/login", data={"username": email_a, "password": "Password123!"}, headers={"Content-Type": "application/x-www-form-urlencoded"}).json()["access_token"]
        auth_a = {"Authorization": f"Bearer {token_a}"}

        # Create User B
        email_b = f"userb_{uuid.uuid4().hex[:6]}@test.com"
        client.post("/users/", json={"first_name": "TestB", "last_name": "UserB", "email": email_b, "password": "Password123!", "phone_number": "000000", "date_of_birth": "1990-01-01", "gender": "Male", "location": "Morocco"})
        token_b = client.post("/auth/login", data={"username": email_b, "password": "Password123!"}, headers={"Content-Type": "application/x-www-form-urlencoded"}).json()["access_token"]
        auth_b = {"Authorization": f"Bearer {token_b}"}

        # --- TEST 1: Greeting ---
        sep("TEST 1: Greeting")
        r = client.post("/rag/chat", json={"question": "Hello!"}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "villastay" in r.json()["answer"].lower() or "villa" in r.json()["answer"].lower()

        # --- TEST 2: What are my bookings? ---
        sep("TEST 2: What are my bookings?")
        r = client.post("/rag/chat", json={"question": "What are my bookings?"}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "no bookings" in r.json()["answer"].lower() or "do not have" in r.json()["answer"].lower() or "couldn't find" in r.json()["answer"].lower() or "could not find" in r.json()["answer"].lower()

        # --- TEST 5: No uploaded documents ---
        sep("TEST 5: What does my uploaded document say? (No docs)")
        r = client.post("/rag/chat", json={"question": "What does my uploaded document say?"}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "find" in r.json()["answer"].lower() or "don't currently have" in r.json()["answer"].lower() or "available" in r.json()["answer"].lower()

        # Upload docs for A
        print("\nUploading docs for User A...")
        r = client.post("/rag/documents", files={"file": ("villa_policy.pdf", VILLA_POLICY, "application/pdf")}, headers=auth_a)
        doc_policy_id = r.json()["id"]
        wait_for_ready(client, auth_a, doc_policy_id)
        
        r = client.post("/rag/documents", files={"file": ("rome.pdf", UNRELATED_PDF, "application/pdf")}, headers=auth_a)
        doc_rome_id = r.json()["id"]
        wait_for_ready(client, auth_a, doc_rome_id)

        # --- TEST 3: What is the cancellation policy in my document? ---
        sep("TEST 3: What is the cancellation policy in my document?")
        r = client.post("/rag/chat", json={"question": "What is the cancellation policy in my document?"}, headers=auth_a)
        ans = r.json()
        print("Answer:", ans["answer"])
        print("Sources:", [s['filename'] for s in ans['sources']])
        assert "48" in ans["answer"].lower()
        assert len(ans["sources"]) > 0

        # --- TEST 4: What does this uploaded PDF talk about? (Implicit) ---
        sep("TEST 4: What does the rome document talk about?")
        r = client.post("/rag/chat", json={"question": "What does the rome document talk about?"}, headers=auth_a)
        ans = r.json()
        print("Answer:", ans["answer"])
        assert "rome" in ans["answer"].lower() or "garum" in ans["answer"].lower()

        # --- TEST 6: Unrelated question ---
        sep("TEST 6: What is the capital of Japan?")
        r = client.post("/rag/chat", json={"question": "What is the capital of Japan?"}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "villastay" in r.json()["answer"].lower() or "unrelated" in r.json()["answer"].lower()

        # --- TEST 7: Programming question ---
        sep("TEST 7: Solve this LeetCode problem")
        r = client.post("/rag/chat", json={"question": "Solve this LeetCode problem in Python"}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "help with unrelated topics" in r.json()["answer"].lower() or "villastay" in r.json()["answer"].lower()

        # --- TEST 9: Document ownership (User B shouldn't see A's docs) ---
        sep("TEST 9: User B asks about cancellation policy")
        r = client.post("/rag/chat", json={"question": "What is the cancellation policy?"}, headers=auth_b)
        print("Answer:", r.json()["answer"])
        assert "48 hours" not in r.json()["answer"].lower()

        # --- TEST 10: Follow-up conversational context ---
        sep("TEST 10: Follow-up context")
        history = [
            {"role": "user", "content": "What is the cancellation policy?"},
            {"role": "assistant", "content": "You can cancel free of charge up to 48 hours before check-in."}
        ]
        r = client.post("/rag/chat", json={"question": "What happens if I do it 24 hours before?", "history": history}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "48" in r.json()["answer"].lower() or "cancel" in r.json()["answer"].lower()
        assert "could not find" not in r.json()["answer"].lower()
        
        # --- TEST 11: Follow-up check-in ---
        sep("TEST 11: Follow-up check-in")
        history = [
            {"role": "user", "content": "What are the villa check-in rules?"},
            {"role": "assistant", "content": "Check-in is strictly at 3 PM."}
        ]
        r = client.post("/rag/chat", json={"question": "What about arriving late?", "history": history}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "8 pm" in r.json()["answer"].lower() or "notice" in r.json()["answer"].lower()
        
        # --- TEST 12: Follow-up guests ---
        sep("TEST 12: Follow-up guests")
        history = [
            {"role": "user", "content": "How many guests are allowed?"},
            {"role": "assistant", "content": "A maximum of 4 guests are allowed per villa."}
        ]
        r = client.post("/rag/chat", json={"question": "What if we bring two more?", "history": history}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "fee" in r.json()["answer"].lower() or "incur" in r.json()["answer"].lower() or "charge" in r.json()["answer"].lower() or "cost" in r.json()["answer"].lower()

        # --- TEST 13: Unrelated inheritance prevention ---
        sep("TEST 13: Unrelated context prevention")
        history = [
            {"role": "user", "content": "What is the capital of Japan?"},
            {"role": "assistant", "content": "I'm here to help with VillaStay — bookings, properties, reservations, rental policies, and rental documents. I can't help with unrelated topics."}
        ]
        r = client.post("/rag/chat", json={"question": "What are the cancellation rules?", "history": history}, headers=auth_a)
        print("Answer:", r.json()["answer"])
        assert "48 hours" in r.json()["answer"].lower() or "cancel" in r.json()["answer"].lower()

        # Generate fake booking for test 8
        print("\nCreating fake booking for User A...")
        client.post("/assets/", json={"name": "Test Villa", "asset_type": "Villa", "location": "Test City", "price_per_night": 100, "max_guests": 4}, headers=auth_a)
        assets = client.get("/assets/", headers=auth_a).json()
        test_asset_id = assets[0]["id"]
        
        booking_payload = {
            "asset_id": test_asset_id,
            "start_date": "2030-01-01",
            "end_date": "2030-01-05",
            "adult_count": 2,
            "child_count": 0,
            "baby_count": 0
        }
        b_res = client.post("/bookings/", json=booking_payload, headers=auth_a)
        booking_id = b_res.json().get("id")

        if booking_id:
            # --- TEST 8: Booking ownership ---
            sep("TEST 8: Booking ownership (User B asks for User A's booking)")
            r = client.post("/rag/chat", json={"question": f"What is the status of booking {booking_id}?"}, headers=auth_b)
            print("Answer:", r.json()["answer"])
            assert "could not find" in r.json()["answer"].lower() or "don't" in r.json()["answer"].lower() or "do not" in r.json()["answer"].lower() or "find that information" in r.json()["answer"].lower()
        else:
            print("Warning: could not create booking for Test 8")

        print("\nALL AGENT TESTS COMPLETED.")

if __name__ == "__main__":
    main()
