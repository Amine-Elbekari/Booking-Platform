import asyncio
from database import AsyncSessionLocal
from datetime import datetime
from models.user import User



async def fill_user_table():

    date_of_birth = datetime.strptime('1999-01-01', '%Y-%m-%d').date()
    print("Opening database session...")
    async with AsyncSessionLocal() as db:
        try:
            new_user = User(
                first_name="Amine",
                last_name="El Bekari",
                email="amine.test@example.com",
                phone_number="+212600000000",
                date_of_birth=date_of_birth,
                gender="Male",
                address="1337 Campus",
                country="Morocco",
                city="Benguerir"
            )

            db.add(new_user)
            await db.commit()

            print(f"SUCCESS! Inserted user: {new_user.first_name} {new_user.last_name}")
            print(f"Generated UUID: {new_user.id}")

        except Exception as e:
            # If we run this twice, Postgres will block it because the email isn't unique!
            await db.rollback()
            print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(fill_user_table())