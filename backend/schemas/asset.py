from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal
# from typing import Optional

class AssetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: str = Field(..., max_length=50)
    location: str = Field(..., max_length=255)
    # i use decimal here because floats lose precision
    price_per_night: Decimal = Field(..., ge=0, description="Price per night must be >= 0")

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)