from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from database import get_db
from pydantic import BaseModel, Field
from datetime import date
from models.user import User
from schemas.user import UserCreate, UserResponse
from .auth import get_current_user
from security import get_password_hash
from uuid import UUID

# all routes here start with /users that's way i put prefix="/users"
router = APIRouter(prefix="/users", tags=["Users"])

class ProfileCompleteSchema(BaseModel):
    phone_number: str = Field(..., example="+212600000000")
    date_of_birth: date = Field(..., example="1998-06-16")
    city: str = Field(..., example="Casablanca")
    country: str = Field(..., example="Morocco")
    gender: str = Field(..., example="Male or Female")

@router.patch("/me/complete-profile")
async def complete_profile(
    payload: ProfileCompleteSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()
    age = today.year - payload.date_of_birth.year - ((today.month, today.day) < (payload.date_of_birth.month, payload.date_of_birth.day))

    if age < 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be at least 18 uears old to make a booking."
        )

    query = (
        update(User)
        .where(User.id == current_user.id)
        .values(
            phone_number = payload.phone_number,
            date_of_birth = payload.date_of_birth,
            city = payload.city,
            country = payload.country,
            gender = payload.gender        
        )
    )
    
    await db.execute(query)
    await db.commit()
    # await db.refresh(current_user)
    
    return {"status": "success", "message": "Profile verified successfully"}
    

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # check if the email already exists in db
    # I use select() here which is async way to query in SQLAlchemy 2
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registred"
        )
    
    # convert the Pydantic JSON into a SQLALcheny Model
    # here .model_dump() unpacks the dictionary automatically
    user_dict = user.model_dump()
    hashed_pass = get_password_hash(user_dict.pop("password"))
    user_dict["hashed_password"] = hashed_pass
    
    new_user = User(**user_dict)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )
    return user