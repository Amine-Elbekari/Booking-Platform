import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from routers import users, assets, bookings, auth

ENV = os.getenv("ENVIRONMENT", "production")

if ENV == "production":
    app = FastAPI(
        title="BooksEasy Architecture API",
        root_path="/api",
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
else:
    app = FastAPI(title="Rental Architecture API", root_path="/api")
    app.add_middleware(
        CORSMiddleware,
        allow_origin=['*'], # don't forget to change it in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# @app.get("/health")
# # inject database session
# async def health_check(db: AsyncSession = Depends(get_db)):
#     try:
#         result = await db.execute(text("SELECT 1"))
#         db_status = "Connected and active!" if result.scalar() == 1 else "Failed"

#         return {
#             "status": "ok",
#             "environment": ENV ,
#             "message": db_status}
#     except Exception as e:
#         return {"status": "Error", "database": str(e)}

app.include_router(users.router)
app.include_router(assets.router)
app.include_router(bookings.router)
app.include_router(auth.router)