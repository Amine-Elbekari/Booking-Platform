import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Initialize SentenceTransformer globally
MODEL_NAME = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
# The huggingface cache volume ensures this isn't downloaded every time
try:
    print(f"Loading embedding model: {MODEL_NAME}")
    embedding_model = SentenceTransformer(MODEL_NAME, device='cpu')
    print("Embedding model loaded successfully.")
except Exception as e:
    print(f"Failed to load embedding model: {e}")
    embedding_model = None

# Initialize ChromaDB Client
try:
    print("Connecting to ChromaDB at host: chroma, port: 8000")
    chroma_client = chromadb.HttpClient(host="chroma", port=8000)
    chroma_client.heartbeat()
    print("ChromaDB connection successful.")
except Exception as e:
    print(f"Failed to connect to ChromaDB: {e}")
    chroma_client = None

def get_embedding_model():
    return embedding_model

def get_chroma_client():
    return chroma_client

def get_or_create_collection(user_id: str):
    """Get or create a Chroma collection for a specific user to ensure isolation."""
    client = get_chroma_client()
    if not client:
        raise Exception("ChromaDB client is not initialized.")
    # We create a single collection and filter by user_id in metadata
    collection_name = "rental_documents"
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def ingest_document_chunks(chunks: list):
    """Embed and store chunks in ChromaDB."""
    if not chunks:
        return
    
    model = get_embedding_model()
    collection = get_or_create_collection(chunks[0]['metadata']['user_id'])
    
    texts = [chunk['text'] for chunk in chunks]
    ids = [chunk['id'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    
    print(f"Generating embeddings for {len(chunks)} chunks...")
    embeddings = model.encode(texts).tolist()
    
    print("Storing chunks in ChromaDB...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )
    print("Ingestion complete.")

def query_documents(user_id: str, query_text: str, active_document_ids: list, top_k: int = 5):
    """Retrieve relevant document chunks for a specific user within active documents."""
    if not active_document_ids:
        return []

    model = get_embedding_model()
    collection = get_or_create_collection(user_id)
    
    query_embedding = model.encode([query_text]).tolist()[0]
    
    if len(active_document_ids) == 1:
        where_clause = {
            "$and": [
                {"user_id": str(user_id)},
                {"document_id": str(active_document_ids[0])}
            ]
        }
    else:
        where_clause = {
            "$and": [
                {"user_id": str(user_id)},
                {"document_id": {"$in": [str(d) for d in active_document_ids]}}
            ]
        }
        
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause # Enforce user isolation and active documents
    )
    
    retrieved_chunks = []
    if results and 'documents' in results and results['documents']:
        for i in range(len(results['documents'][0])):
            retrieved_chunks.append({
                "id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results.get('metadatas') else {}
            })
            
    return retrieved_chunks

