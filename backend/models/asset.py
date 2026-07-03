import uuid
from sqlalchemy import Column, String, Numeric, DateTime, func, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    asset_type = Column(String, nullable=False)
    location = Column(String(255), nullable=False)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    max_guests = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
