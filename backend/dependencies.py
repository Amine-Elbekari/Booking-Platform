import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.user import User
from security import SECRET_KEY, ALGORITHM

# Tell FastAPI to look for the token in the 'Authorization: Bearer '<token>' header.
# The tokenUrl tells Swagger UI where to send the login request when you click "Authorize".

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token using the static Secret Key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Store the user's ID inside the 'sub' (subject) claim of the JWT
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status=401, detail="Token has expired. Please log in again.")
    except jwt.PyJWTError:
        # catch fake or tampered token
        raise credentials_exception
    
    # Check if the user still exists in the database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user