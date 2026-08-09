# Manage the connection pool to the database
import os
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Build the connection URL
# the host here is name service from docker-compose
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
# Create the Async engine
# this is the actula engine that talks to postgres
# i put echo=True for debugging so all the,
# generated SQL will be printed to terminal
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the Session Factory
# this generates a temporary sessions with the database,
# every time a user makes a request
# expire_on_commit=False ensures the data is always available for FastAPI to send
# back to the user
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Create the Declarative Base
# declarative_base is a factory function used to construct 
# a base class for ORM class definitions
# it acts as a translator and orgnizer byt creating,
# a blueprint that connects python classes to db tables
# so it know that for example class User belongs to a table named users with
# with specific columns

Base = declarative_base()

# Dependency Injection
# inject this function  into our routes,
# so they can access the database safely 
# This function manages the lifecycle of database connections,
# it acts like a temporary bridge built for one single HTTP request
# and it gets torn down the moment that request is finished

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis():
    client = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_response=True)
    try:
        yield client
    finally:
        await client.aclose()