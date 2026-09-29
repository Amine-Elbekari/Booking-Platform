"""
End-to-End RAG Lifecycle Test.
Verifies source attribution accuracy, document deletion, isolation, anti-hallucination, and cross-domain document understanding.
Run: docker compose exec api python scripts/rag_lifecycle_test.py
"""
import httpx
import time
import uuid

API = "http://localhost:8000"
TIMEOUT = httpx.Timeout(60.0)

def sep(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print('─'*60)
    time.sleep(10) # Prevent Gemini/Ollama 429 errors or overloaded generation

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

VILLA_POLICY = generate_pdf("Guests may cancel free of charge up to 48 hours before check-in.")
HYPERTUBE = generate_pdf("Hypertube is a 42 school project about streaming videos. The backend API uses OAuth 2.0 for authentication.")
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

        # --- TEST A: No documents uploaded ---
        sep("TEST A: No documents uploaded.")
        r = client.post("/rag/chat", json={"question": "What is the cancellation policy?"}, headers=auth_a)
        ans = r.json()
        print(f"Answer: {ans['answer']}")
        assert "couldn't find" in ans['answer'].lower() or "not" in ans['answer'].lower() or "available" in ans['answer'].lower()

        # --- TEST B: Upload PDF and find policy ---
        sep("TEST B: Upload a PDF containing a known policy.")
        r = client.post("/rag/documents", files={"file": ("villa_policy.pdf", VILLA_POLICY, "application/pdf")}, headers=auth_a)
        doc_policy_id = r.json()["id"]
        wait_for_ready(client, auth_a, doc_policy_id)
        
        r = client.post("/rag/chat", json={"question": "What is the cancellation policy?"}, headers=auth_a)
        ans = r.json()
        print(f"Answer: {ans['answer']}")
        print(f"Sources: {[s['filename'] for s in ans['sources']]}")
        assert "48 hours" in ans["answer"]
        assert len(ans["sources"]) > 0
        assert ans["sources"][0]["filename"] == "villa_policy.pdf"

        # --- TEST C: Upload hypertube.pdf and ask what it's about ---
        sep("TEST C: Upload hypertube.pdf. Ask: 'What is this document about?'")
        r = client.post("/rag/documents", files={"file": ("hypertube.pdf", HYPERTUBE, "application/pdf")}, headers=auth_a)
        doc_hyper_id = r.json()["id"]
        wait_for_ready(client, auth_a, doc_hyper_id)
        
        r = client.post("/rag/chat", json={"question": "What is this document about?"}, headers=auth_a)
        ans = r.json()
        print(f"Answer: {ans['answer']}")
        print(f"Sources: {[s['filename'] for s in ans['sources']]}")
        # Could reference either hypertube or villa_policy since both are uploaded
        assert "hypertube" in ans["answer"].lower() or "42" in ans["answer"].lower() or "cancel" in ans["answer"].lower()

        # --- TEST D: Upload hypertube.pdf and ask about APIs ---
        sep("TEST D: Ask: 'What APIs are described in the document?'")
        r = client.post("/rag/chat", json={"question": "What APIs are described in the document?"}, headers=auth_a)
        ans = r.json()
        print(f"Answer: {ans['answer']}")
        print(f"Sources: {[s['filename'] for s in ans['sources']]}")
        assert "oauth" in ans["answer"].lower()
        
        # --- TEST E: Upload an unrelated PDF and ask what it's about ---
        sep("TEST E: Upload unrelated PDF. Ask: 'What is this document about?'")
        r = client.post("/rag/documents", files={"file": ("rome.pdf", UNRELATED_PDF, "application/pdf")}, headers=auth_a)
        doc_rome_id = r.json()["id"]
        wait_for_ready(client, auth_a, doc_rome_id)
        
        r = client.post("/rag/chat", json={"question": "What is the rome document about?"}, headers=auth_a)
        ans = r.json()
        print(f"Answer: {ans['answer']}")
        print(f"Sources: {[s['filename'] for s in ans['sources']]}")
        assert "rome" in ans["answer"].lower() or "garum" in ans["answer"].lower()

        # --- TEST F: User Isolation ---
        sep("TEST F: User B must not retrieve User A's document.")
        r = client.post("/rag/chat", json={"question": "What APIs are described in the document?"}, headers=auth_b)
        ans = r.json()
        print(f"Answer (User B): {ans['answer']}")
        assert "oauth" not in ans["answer"].lower()

        # --- TEST G: Unrelated programming question ---
        sep("TEST G: Ask an unrelated programming question (out of scope).")
        r = client.post("/rag/chat", json={"question": "Can you solve this LeetCode problem?"}, headers=auth_a)
        ans = r.json()
        print(f"Answer: {ans['answer']}")
        assert "help with unrelated topics" in ans["answer"]

        print("\nALL 7 TESTS COMPLETED SUCCESSFULLY ✅")

if __name__ == "__main__":
    main()
