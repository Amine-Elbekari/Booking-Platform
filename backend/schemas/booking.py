from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

class BookingBase(BaseModel):
    start_date: date
    end_date: date
    adult_count: int = Field(default=1, ge=1)
    child_count: int = Field(default=0, ge=0)
    baby_count: int = Field(default=0, ge=0)

class BookingCreate(BookingBase):
    asset_id: UUID
    user_id: UUID

    # for security i don't put 'total_price' or 'status' here,
    # if i did, a hacker could send a JSON payload with {total_price = 0.00}
    # and book the assets for free

class BookingResponse(BookingBase):
    id: UUID
    asset_id: UUID
    user_id: UUID

    # i send these back , but there were calculated safely in my Python logic,
    # not trusted from the frontend
    total_price: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
