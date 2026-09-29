from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

class AgentDecision(BaseModel):
    intent: Literal["DOCUMENTS", "BOOKINGS", "PROPERTY", "GENERAL_VILLASTAY", "UNRELATED"]
    tool: Optional[Literal["search_documents", "get_user_bookings", "get_booking", "get_property"]] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
