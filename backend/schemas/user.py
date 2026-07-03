from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID

# Shared fields

class UserBase(BaseModel):
    # ... means that this field is required 
    first_name: str = Field(..., min_length=2, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(..., description="Valid email address format required")
    phone_number: str = Field(..., max_length=20)

    date_of_birth: date
    gender: str = Field(..., max_length=20)

    address: Optional[str] = None
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)

# Create Model (Incoming from Vite/React)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Must be at least 8 characters")

# The Response Model (Outgoing to Vite/React)
class UserResponse(UserBase):

    id: UUID
    created_at: datetime

    
       # i add the 'model_config' to prevent pydentic form crash,
       # when querring the database using Python driver,
       # like asyncpg , the database does not return a standard
       # Python dictionary, ir returns a Record Object to Pydanting
       # will use the dot notation instead of looking for keys 
    
    model_config = ConfigDict(from_attributes=True)