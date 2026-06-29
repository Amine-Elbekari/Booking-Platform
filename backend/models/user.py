import uuid
from sqlalchemy import Column, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # index=true makes searching by email fast
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    address = Column(String(255))
    country = Column(String(100))
    city = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
