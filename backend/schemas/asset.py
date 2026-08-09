from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class AssetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    asset_type: str = Field(..., max_length=50)
    location: str = Field(..., max_length=255)
    price_per_night: Decimal = Field(..., ge=0, description="Price per night must be >= 0")
    max_guests: int = Field(..., ge=1, description="Max guests must be >= 1")
    is_active: bool = Field(default=True)

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssetAvailabilityResponse(BaseModel):
    asset_id: UUID
    available: bool