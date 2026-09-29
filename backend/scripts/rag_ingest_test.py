"""
Quick test: manually run the background task pipeline inline to see what error surfaces.
"""
import asyncio, os, sys
sys.path.insert(0, '/app')

os.environ.setdefault('DATABASE_URL', os.getenv('DATABASE_URL', ''))

from services.rag_processor import process_document
from services.rag_service import ingest_document_chunks, get_chroma_client

# Use a tiny fake PDF to test ingestion directly
FAKE_PDF_CONTENT = b"""\
%PDF-1.4
1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj
2 0 obj<</Type /Pages /Kids[3 0 R] /Count 1>>endobj
3 0 obj<</Type /Page /Parent 2 0 R /MediaBox[0 0 612 792]
/Contents 4 0 R /Resources<</Font<</F1<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>>>>>>>endobj
4 0 obj<</Length 120>>stream
BT /F1 12 Tf 100 700 Td
(Cancellation Policy: Free cancellation up to 48 hours before check-in.) Tj
ET
endstream endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
trailer<</Size 5 /Root 1 0 R>>
startxref
446
%%EOF"""

TEST_USER_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TEST_DOC_ID  = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

print("\n=== TEST: Direct ingestion pipeline ===")
print("Step 1: process_document()")
try:
    chunks = process_document(FAKE_PDF_CONTENT, "test_policy.pdf", TEST_USER_ID, TEST_DOC_ID)
    print(f"  Chunks produced: {len(chunks)}")
    for c in chunks[:2]:
        print(f"  Chunk text: {c['text'][:100]!r}")
        print(f"  Metadata:   {c['metadata']}")
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\nStep 2: ingest_document_chunks()")
try:
    ingest_document_chunks(chunks)
    print("  Ingestion: OK")
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\nStep 3: verify stored count")
client = get_chroma_client()
collection = client.get_collection("rental_documents")
count = collection.count()
print(f"  Total chunks in collection: {count}")

# Clean up test data
print("\nStep 4: clean up test data")
try:
    all_ids = collection.get(where={"user_id": TEST_USER_ID})["ids"]
    if all_ids:
        collection.delete(ids=all_ids)
        print(f"  Deleted {len(all_ids)} test chunk(s)")
except Exception as e:
    print(f"  Cleanup note: {e}")

print("\n=== Done. If all steps passed, the ingestion code is OK. ===")
print("The bug must be in how the background task accesses the DB session.")
