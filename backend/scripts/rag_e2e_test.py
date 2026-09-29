"""
End-to-end RAG pipeline test.
Creates a user, uploads a test PDF document, waits for READY status,
then runs 4 test queries and prints full diagnostic output.

Run: docker compose exec api python scripts/rag_e2e_test.py
"""
import asyncio
import httpx
import sys
import time
import uuid

API = "http://localhost:8000"
TIMEOUT = httpx.Timeout(60.0)

# A minimal valid PDF with rental policy content
PDF_CONTENT = b"""%PDF-1.4
1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj
2 0 obj<</Type /Pages /Kids[3 0 R] /Count 1>>endobj
3 0 obj<</Type /Page /Parent 2 0 R /MediaBox[0 0 612 792] /Contents 4 0 R /Resources<</Font<</F1<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>>>>>  >>endobj
4 0 obj<</Length 395>>stream
BT /F1 11 Tf 50 750 Td
(VILLA RENTAL POLICIES) Tj 0 -25 Td
(Cancellation Policy: Guests may cancel free of charge up to 48 hours before check-in.) Tj 0 -25 Td
(After that period, one night will be charged as a cancellation fee.) Tj 0 -25 Td
(Check-in: Check-in time is from 3:00 PM onwards.) Tj 0 -25 Td
(Check-out: Check-out time is before 11:00 AM.) Tj 0 -25 Td
(Pets: Pets are not allowed on the property.) Tj 0 -25 Td
(Smoking: Smoking is strictly prohibited inside the villa.) Tj
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
%%EOF"""


def sep(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print('─'*60)


async def main():
    unique = str(uuid.uuid4())[:8]
    email = f"ragtest_{unique}@example.com"
    password = "TestPass123!"

    async with httpx.AsyncClient(base_url=API, timeout=TIMEOUT) as client:

        # ── 1. Register & login ────────────────────────────────
        sep("STEP 1: Create test user")
        r = client.post("/users", json={
            "first_name": "Test", "last_name": "User",
            "email": email, "password": password,
            "phone_number": "0000000000",
            "date_of_birth": "1990-01-01",
            "gender": "Male"
        })
        if r.status_code not in (200, 201):
            print(f"Register failed: {r.status_code} {r.text}")
            sys.exit(1)
        print(f"Registered: {email}")

        r = client.post("/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if r.status_code != 200:
            print(f"Login failed: {r.status_code} {r.text}")
            sys.exit(1)
        token = r.json()["access_token"]
        auth = {"Authorization": f"Bearer {token}"}
        print("Login: OK")

        # ── 2. Upload document ─────────────────────────────────
        sep("STEP 2: Upload test PDF")
        r = client.post("/rag/documents",
            files={"file": ("villa_policy.pdf", PDF_CONTENT, "application/pdf")},
            headers=auth)
        if r.status_code not in (200, 201):
            print(f"Upload failed: {r.status_code} {r.text}")
            sys.exit(1)
        doc_id = r.json()["id"]
        print(f"Uploaded document ID: {doc_id}")

        # ── 3. Wait for READY ──────────────────────────────────
        sep("STEP 3: Wait for background processing (READY)")
        for attempt in range(20):
            time.sleep(3)
            r = client.get("/rag/documents", headers=auth)
            docs = r.json()
            doc = next((d for d in docs if d["id"] == doc_id), None)
            status = doc["status"] if doc else "NOT_FOUND"
            print(f"  [{attempt+1}/20] Status: {status}")
            if status == "READY":
                print("  ✓ Document is READY")
                break
            if status == "FAILED":
                print("  ✗ Document FAILED to process — check API logs")
                sys.exit(1)
        else:
            print("  ✗ Timed out waiting for READY")
            sys.exit(1)

        # ── 4. Run queries ─────────────────────────────────────
        questions = [
            "What is the cancellation policy?",
            "When is check-in?",
            "What time do I need to check out?",
            "Tell me the wifi password for the main router.",
        ]

        for q in questions:
            sep(f"QUERY: {q}")
            r = client.post("/rag/chat", json={"question": q}, headers=auth)
            if r.status_code != 200:
                print(f"  ERROR {r.status_code}: {r.text}")
                continue
            data = r.json()
            print(f"ANSWER:\n  {data['answer']}")
            if data.get("sources"):
                print("SOURCES:")
                for src in data["sources"]:
                    print(f"  • {src['filename']}" + (f" p.{src['page']}" if src.get('page') else ""))
            else:
                print("SOURCES: none")


if __name__ == "__main__":
    # httpx in sync mode for simplicity inside the container
    import httpx as _httpx

    unique = str(uuid.uuid4())[:8]
    email = f"ragtest_{unique}@example.com"
    password = "TestPass123!"

    def sep(title):
        print(f"\n{'─'*60}")
        print(f"  {title}")
        print('─'*60)

    with _httpx.Client(base_url=API, timeout=TIMEOUT, follow_redirects=True) as client:

        sep("STEP 1: Create test user")
        r = client.post("/users", json={
            "first_name": "Test", "last_name": "User",
            "email": email, "password": password,
            "phone_number": "0000000000",
            "date_of_birth": "1990-01-01",
            "gender": "Male"
        })
        if r.status_code not in (200, 201):
            print(f"Register failed: {r.status_code} {r.text}"); sys.exit(1)
        print(f"Registered: {email}")

        r = client.post("/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if r.status_code != 200:
            print(f"Login failed: {r.status_code} {r.text}"); sys.exit(1)
        token = r.json()["access_token"]
        auth = {"Authorization": f"Bearer {token}"}
        print("Login: OK")

        sep("STEP 2: Upload test PDF")
        r = client.post("/rag/documents",
            files={"file": ("villa_policy.pdf", PDF_CONTENT, "application/pdf")},
            headers=auth)
        if r.status_code not in (200, 201):
            print(f"Upload failed: {r.status_code} {r.text}"); sys.exit(1)
        doc_id = r.json()["id"]
        print(f"Uploaded document ID: {doc_id}")

        sep("STEP 3: Wait for background processing (READY)")
        for attempt in range(20):
            time.sleep(3)
            r = client.get("/rag/documents", headers=auth)
            docs = r.json()
            doc = next((d for d in docs if d["id"] == doc_id), None)
            status = doc["status"] if doc else "NOT_FOUND"
            print(f"  [{attempt+1}/20] Status: {status}")
            if status == "READY":
                print("  ✓ Document is READY"); break
            if status == "FAILED":
                print("  ✗ Document FAILED — check API logs"); sys.exit(1)
        else:
            print("  ✗ Timed out waiting for READY"); sys.exit(1)

        questions = [
            "What is the cancellation policy?",
            "When is check-in?",
            "What time do I need to check out?",
            "Tell me the wifi password for the main router.",
        ]

        for q in questions:
            sep(f"QUERY: {q}")
            r = client.post("/rag/chat", json={"question": q}, headers=auth)
            if r.status_code != 200:
                print(f"  ERROR {r.status_code}: {r.text}"); continue
            data = r.json()
            print(f"ANSWER:\n  {data['answer']}")
            if data.get("sources"):
                print("SOURCES:")
                for src in data["sources"]:
                    page = f" (page {src['page']})" if src.get('page') else ""
                    print(f"  • {src['filename']}{page}")

        print("\n" + "="*60)
        print("  E2E TEST COMPLETE")
        print("="*60)
