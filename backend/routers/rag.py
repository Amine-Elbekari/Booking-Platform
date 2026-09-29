import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List
from database import get_db, AsyncSessionLocal, get_redis
from redis.asyncio import Redis
from datetime import date
from routers.auth import get_current_user
from models.user import User
from models.document import Document
from schemas.rag import DocumentResponse, ChatRequest, ChatResponse, Source
from services.rag_processor import process_document
from services.rag_service import ingest_document_chunks, query_documents, get_embedding_model, get_chroma_client
import asyncio
import os
import requests

router = APIRouter(prefix="/rag", tags=["RAG"])

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 5))
FREE_UPLOADS_PER_DAY = int(os.getenv("FREE_UPLOADS_PER_DAY", 5))

@router.get("/health")
async def rag_health():
    model = get_embedding_model()
    client = get_chroma_client()
    
    return {
        "embedding_model_loaded": model is not None,
        "chromadb_connected": client is not None
    }

async def process_document_background(file_bytes: bytes, filename: str, user_id: str, document_id: str):
    """
    Background task that owns its own DB session.
    The request-scoped session is already closed by the time this runs,
    so we must create a fresh one here using the session factory directly.
    """
    async with AsyncSessionLocal() as db:
        try:
            print(f"[BG] Starting processing for document {document_id}")
            
            # Extract and chunk
            chunks = process_document(file_bytes, filename, user_id, document_id)
            print(f"[BG] Extracted {len(chunks)} chunks from '{filename}'")
            
            # Embed and store in ChromaDB
            ingest_document_chunks(chunks)
            print(f"[BG] Chunks stored in ChromaDB")
            
            # Mark as READY in PostgreSQL
            await db.execute(update(Document).where(Document.id == document_id).values(status='READY'))
            await db.commit()
            print(f"[BG] Document {document_id} marked as READY")
        except Exception as e:
            import traceback
            print(f"[BG] Error processing document {document_id}: {e}")
            traceback.print_exc()
            try:
                await db.execute(update(Document).where(Document.id == document_id).values(status='FAILED'))
                await db.commit()
            except Exception as db_err:
                print(f"[BG] Could not mark document as FAILED: {db_err}")


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    if not file.filename.lower().endswith(('.pdf', '.csv')):
        raise HTTPException(status_code=400, detail="Only PDF and CSV files are supported.")
        
    # Rate Limiting
    today = date.today().isoformat()
    rate_limit_key = f"rag_uploads:{current_user.id}:{today}"
    upload_count = await redis.incr(rate_limit_key)
    if upload_count == 1:
        await redis.expire(rate_limit_key, 86400) # 24 hours
        
    if upload_count > FREE_UPLOADS_PER_DAY:
        raise HTTPException(status_code=429, detail=f"Daily upload limit of {FREE_UPLOADS_PER_DAY} reached.")

    file_bytes = await file.read()
    
    # Validation
    if len(file_bytes) == 0:
        await redis.decr(rate_limit_key)
        raise HTTPException(status_code=400, detail="File is empty.")
        
    if len(file_bytes) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        await redis.decr(rate_limit_key)
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {MAX_UPLOAD_SIZE_MB}MB.")
        
    if file.filename.lower().endswith('.pdf'):
        if not file_bytes.startswith(b'%PDF-'):
            await redis.decr(rate_limit_key)
            raise HTTPException(status_code=400, detail="Invalid PDF file format.")
    
    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        status='UPLOADED'
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    background_tasks.add_task(
        process_document_background,
        file_bytes,
        file.filename,
        str(current_user.id),
        str(new_doc.id)
        # NOTE: db is intentionally NOT passed — the background task
        # creates its own session via AsyncSessionLocal to avoid
        # using a closed request-scoped session.
    )
    
    return new_doc

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.user_id == current_user.id))
    docs = result.scalars().all()
    return docs

@router.post("/chat", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from agent.orchestrator import run_agent_loop
    return await run_agent_loop(request, current_user, db)

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format.")
        
    result = await db.execute(select(Document).where(Document.id == doc_uuid, Document.user_id == current_user.id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or you do not have permission to delete it.")
        
    # Delete from ChromaDB
    try:
        client = get_chroma_client()
        if client:
            collection = client.get_or_create_collection(
                name="rental_documents",
                metadata={"hnsw:space": "cosine"}
            )
            collection.delete(
                where={
                    "$and": [
                        {"document_id": str(document_id)},
                        {"user_id": str(current_user.id)}
                    ]
                }
            )
            print(f"Deleted vectors for document {document_id}")
    except Exception as e:
        print(f"Error deleting from ChromaDB: {e}")
        # Proceed with DB deletion to not leave orphaned records
        
    # Delete from PostgreSQL
    await db.delete(doc)
    await db.commit()
    
    return None

