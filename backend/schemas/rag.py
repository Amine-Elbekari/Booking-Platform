from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageInfo(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[MessageInfo]] = []

class Source(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    row: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
