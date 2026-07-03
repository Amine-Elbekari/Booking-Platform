from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.asset import Asset
from schemas.asset import AssetCreate, AssetResponse

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
