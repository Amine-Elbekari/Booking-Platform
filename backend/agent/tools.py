import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from models.document import Document
from services.rag_service import query_documents

async def tool_search_documents(query: str, current_user_id: str, db: AsyncSession):
    # 1. Fetch active documents for this user
    result = await db.execute(select(Document).where(Document.user_id == uuid.UUID(current_user_id), Document.status == 'READY'))
    active_docs = result.scalars().all()
    
    if not active_docs:
        return {"status": "error", "message": "You don't currently have any uploaded documents available for me to search. You can upload a rental document and I'll use it as context for your questions."}
        
    active_doc_ids = [str(doc.id) for doc in active_docs]
    
    # 2. Query ChromaDB
    chunks = query_documents(current_user_id, query, active_doc_ids, top_k=5)
    
    if not chunks:
        return {"status": "empty", "message": "I couldn't find that information in your uploaded documents."}
        
    # Return formatted chunks for the LLM
    context_parts = []
    sources = []
    
    for chunk in chunks:
        chunk_id = chunk['id']
        metadata = chunk['metadata']
        context_parts.append(f"--- SOURCE ID: {chunk_id} ({metadata.get('filename', 'Unknown')} p.{metadata.get('page', '?')}) ---\n{chunk['text']}")
        sources.append({
            "document_id": str(metadata.get('document_id', '')),
            "filename": metadata.get('filename', 'Unknown'),
            "page": metadata.get('page'),
            "row": metadata.get('row'),
            "chunk_id": chunk_id
        })
        
    return {
        "status": "success", 
        "context": "\n\n".join(context_parts),
        "sources": sources
    }

async def tool_get_user_bookings(current_user_id: str, db: AsyncSession):
    bookings_query = text("""
        SELECT b.id, b.booking_dates, b.status, b.total_price, a.name, a.location 
        FROM bookings b 
        JOIN assets a ON b.asset_id = a.id 
        WHERE b.user_id = :user_id 
        ORDER BY b.created_at DESC 
        LIMIT 10
    """)
    booking_rows = await db.execute(bookings_query, {"user_id": current_user_id})
    b_results = booking_rows.fetchall()
    
    if not b_results:
        return {"status": "empty", "message": "You do not have any bookings."}
        
    context = "--- USER BOOKINGS ---\n"
    for row in b_results:
        context += f"Booking ID: {row.id} | Villa: {row.name} ({row.location}) | Dates: {row.booking_dates} | Status: {row.status} | Total: ${row.total_price}\n"
        
    return {"status": "success", "context": context}

async def tool_get_booking(booking_id: str, current_user_id: str, db: AsyncSession):
    booking_query = text("""
        SELECT b.id, b.booking_dates, b.status, b.total_price, a.name, a.location, b.adult_count, b.child_count, b.baby_count
        FROM bookings b 
        JOIN assets a ON b.asset_id = a.id 
        WHERE b.id = :booking_id AND b.user_id = :user_id
    """)
    try:
        booking_uuid = uuid.UUID(booking_id)
    except ValueError:
        return {"status": "error", "message": "Invalid booking ID format."}
        
    booking_rows = await db.execute(booking_query, {"booking_id": str(booking_uuid), "user_id": current_user_id})
    row = booking_rows.fetchone()
    
    if not row:
        return {"status": "empty", "message": "I could not find a booking with that ID belonging to you."}
        
    context = f"--- BOOKING DETAILS ---\nBooking ID: {row.id}\nVilla: {row.name} ({row.location})\nDates: {row.booking_dates}\nStatus: {row.status}\nTotal Price: ${row.total_price}\nGuests: {row.adult_count} Adults, {row.child_count} Children, {row.baby_count} Babies"
    return {"status": "success", "context": context}

async def tool_get_property(search_term: str, db: AsyncSession):
    property_query = text("""
        SELECT name, asset_type, location, price_per_night, max_guests, is_active
        FROM assets
        WHERE name ILIKE :search OR location ILIKE :search
        LIMIT 5
    """)
    asset_rows = await db.execute(property_query, {"search": f"%{search_term}%"})
    results = asset_rows.fetchall()
    
    if not results:
        return {"status": "empty", "message": f"I couldn't find any properties matching '{search_term}'."}
        
    context = f"--- PROPERTY SEARCH RESULTS ('{search_term}') ---\n"
    for row in results:
        context += f"Name: {row.name}\nType: {row.asset_type}\nLocation: {row.location}\nPrice per night: ${row.price_per_night}\nMax Guests: {row.max_guests}\nActive: {row.is_active}\n\n"
        
    return {"status": "success", "context": context.strip()}
