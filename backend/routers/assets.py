from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text # for row SQL
from typing import List
from datetime import date
from uuid import UUID
import json

from database import get_db, get_redis
from redis.asyncio import Redis
from models.asset import Asset
from schemas.asset import AssetCreate, AssetResponse, AssetAvailabilityResponse

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: AssetCreate, db: AsyncSession = Depends(get_db)):
    
    # convert Pydantic JSON to SQLAlchemy Model
    new_asset = Asset(**asset.model_dump())

    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)

    return new_asset

# Here the response Model is a List
@router.get("/", response_model=List[AssetResponse], status_code=status.HTTP_200_OK)
async def get_all_assets(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Asset))

    # .scalars.all() graps all row and puts them in a python list
    assets = result.scalars().all()
    return assets


@router.get("/{asset_id}/availability", response_model=AssetAvailabilityResponse, status_code=status.HTTP_200_OK)
async def check_asset_availability(asset_id: UUID, start: date, end: date, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    # validate if that dates make sense
    if start >= end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    cache_key = f"cache:availability:{asset_id}:{start}:{end}"
    cached_result = await redis.get(cache_key)
    if cached_result is not None:
        return AssetAvailabilityResponse(
            asset_id=asset_id,
            available=(cached_result == "true")
        )

    # raw SQL query using the && overlap operator
    # EXISTS return True if there is an overlapping booking.
    query = text("""
        SELECT EXISTS (
            SELECT 1 FROM bookings
            WHERE asset_id = :asset_id
            AND status != 'cancelled'
            AND booking_dates && daterange(:start, :end, '[)')
        )
    """)

    result = await db.execute(query, {
        "asset_id": str(asset_id),
        "start": start,
        "end": end
    })

    # The asset is available if there is NO overlap
    is_overlapping = result.scalar()
    is_available = not is_overlapping
    
    # Cache the result for 30 seconds
    await redis.set(cache_key, "true" if is_available else "false", ex=30)

    return AssetAvailabilityResponse(
        asset_id=asset_id,
        available=is_available
    )