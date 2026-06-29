from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID

class BookingGuestBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr

class BookingGuestCreate(BaseModel):
    # there is not 'booking_id' here because in a,
    # RESTful API the booking ID comes from the URL
    # (e.g., POST /bookings/{booking_id}/guests), not from the JSON body

    pass

class BookingGuestResponse(BaseModel):
    id: UUID
    booking_id: UUID

    model_config = ConfigDict(from_attributes=True)