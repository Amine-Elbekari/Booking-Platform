import os
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
# from jose import jwt, JWTError
import jwt
from database import get_db
from models.user import User
from security import verify_password, create_access_token

router = APIRouter(prefix='/auth', tags=["Authentication"])
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/google")
async def google_login(token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    try:
        # Verify the token with google's servers
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        # Extract user info from Google's verified payload
        email = idinfo.get('email')
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            # Create a new User if he or she is not exists (ofc using a random hard to guess passw since he or she use google)
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                hashed_password="OAUTH_GOOGLE_EXTERNAL_ACCOUNT",
                phone_number=None,
                date_of_birth=None,
                city=None,
                country=None,
                gender=None
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        access_token = create_access_token(data={"sub": str(user.id)})
            
        # check if the user is missing any required onboarding data
        profile_incomplete = not ([
            user.phone_number and str(user.phone_number).strip() and
            user.date_of_birth and
            user.city and str(user.city).strip() and
            user.country and str(user.country).strip() and
            user.gender and str(user.gender).strip()
        ])
            
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "requires_onboarding": profile_incomplete
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Authentication Token")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # find the user by email (OAuth2 uses the 'username' field for identifier which holds the user's email)
    
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate the JWT using the user's UUID
    access_token = create_access_token({"sub": str(user.id)})
    # Return the standard OAuth2 token response
    
    profile_incomplete = not all ([
        user.phone_number,
        user.date_of_birth,
        user.city,
        user.country,
        user.gender
    ])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "required_onboarding": profile_incomplete
    }

async def get_current_user(token: str = Depends(oauth_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token and extract the subject payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    # Query db using the UUID found in the token paylaod
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    return user    