"""
RAG Pipeline Diagnostic Script
Traces a complete query from embedding → ChromaDB → Gemini
Run with: docker compose exec api python scripts/rag_debug.py
"""
import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION_NAME = "rental_documents"

def divider(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def main():
    question = "What is the cancellation policy?"
    
    divider("1. EMBEDDING MODEL")
    print(f"Model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, device='cpu')
    query_embedding = model.encode([question]).tolist()[0]
    print(f"Embedding dimensions: {len(query_embedding)}")
    print(f"First 5 values: {query_embedding[:5]}")

    divider("2. CHROMADB CONNECTION")
    client = chromadb.HttpClient(host="chroma", port=8000)
    client.heartbeat()
    print("ChromaDB connection: OK")

    divider("3. ALL COLLECTIONS IN CHROMADB")
    collections = client.list_collections()
    if not collections:
        print("⚠ NO COLLECTIONS FOUND - no documents have been ingested!")
        return
    for col in collections:
        print(f"  Collection: {col.name}")

    divider("4. INSPECT COLLECTION: rental_documents")
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as e:
        print(f"⚠ Collection '{COLLECTION_NAME}' not found: {e}")
        return

    count = collection.count()
    print(f"Total chunks stored: {count}")

    if count == 0:
        print("⚠ COLLECTION IS EMPTY - no chunks have been ingested!")
        return

    divider("5. SAMPLE STORED CHUNK (first result)")
    sample = collection.get(limit=3, include=["documents", "metadatas"])
    for i, (doc, meta) in enumerate(zip(sample['documents'], sample['metadatas'])):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Metadata: {meta}")
        print(f"Text[:200]: {doc[:200]}")

    divider("6. ALL UNIQUE USER IDs IN COLLECTION")
    all_items = collection.get(include=["metadatas"])
    user_ids = set(m.get("user_id", "?") for m in all_items["metadatas"])
    print(f"User IDs with stored data: {user_ids}")

    divider("7. RAW QUERY (no user_id filter)")
    raw_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )
    if raw_results["documents"][0]:
        for i, (doc, meta, dist) in enumerate(zip(
            raw_results["documents"][0],
            raw_results["metadatas"][0],
            raw_results["distances"][0]
        )):
            print(f"\n--- Result {i+1} ---")
            print(f"Distance: {dist:.4f}  (lower=better for cosine space in Chroma)")
            print(f"Metadata: {meta}")
            print(f"Text[:300]: {doc[:300]}")
    else:
        print("No results from raw query!")

    divider("8. FILTERED QUERY (with user_id from stored data)")
    if user_ids:
        test_user_id = list(user_ids)[0]
        print(f"Testing with user_id: {test_user_id}")
        filtered_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where={"user_id": str(test_user_id)},
            include=["documents", "metadatas", "distances"]
        )
        if filtered_results["documents"][0]:
            for i, (doc, meta, dist) in enumerate(zip(
                filtered_results["documents"][0],
                filtered_results["metadatas"][0],
                filtered_results["distances"][0]
            )):
                print(f"\n--- Result {i+1} ---")
                print(f"Distance: {dist:.4f}")
                print(f"Metadata: {meta}")
                print(f"Text[:300]: {doc[:300]}")
        else:
            print(f"⚠ No results for user_id={test_user_id}")

    divider("9. CONCLUSION")
    print("Check the results above:")
    print("- If section 3 shows NO collections → documents are not being ingested.")
    print("- If section 4 count is 0 → ingestion is failing (check API logs).")
    print("- If section 7 returns results but section 8 does not →")
    print("  the user_id used at query time doesn't match the user_id stored during ingestion.")
    print("- If distances > 1.5 in cosine space → the wrong space type may be in use.")

if __name__ == "__main__":
    main()
