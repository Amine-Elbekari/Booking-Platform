from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from database import get_db
from schemas.booking import BookingCreate
from dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    if str(booking.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only create bookings for your own account.")
    
    delta = booking.end_date - booking.start_date
    total_days = delta.days # days property from timedelta object generated under the hood by python

    if total_days <= 0:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    try:
        # we lock the asset here to get the price safely
        lock_query = text("""
            SELECT price_per_night
            FROM assets
            WHERE id = :asset_id
            FOR UPDATE
        """)
        result = await db.execute(lock_query, {"asset_id": str(booking.asset_id)})
        asset = result.fetchone()

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        total_price = asset[0] * total_days
        
        # insert the booking
        # I use daterange(:start_date, :end_date, '[)') inside the sql
        insert_query = text("""
            INSERT INTO bookings (
                user_id, asset_id, booking_dates, total_price,
                adult_count, child_count, baby_count, status          
            )
            VALUES (
                :user_id, :asset_id, daterange(:start_date, :end_date, '[)'), :total_price,
                :adult_count, :child_count, :baby_count, 'pending'
            )
            RETURNING id, created_at
        """)

        booking_result = await db.execute(insert_query, {
            "user_id": str(booking.user_id),
            "asset_id": str(booking.asset_id),
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "total_price": total_price,
            "adult_count": booking.adult_count,
            "child_count": booking.child_count,
            "baby_count": booking.baby_count
        })

        new_booking = booking_result.fetchone()

        await db.commit()

        return {
            "id": new_booking[0],
            "asset_id": booking.asset_id,
            "user_id": booking.user_id,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "adult_count": booking.adult_count,
            "child_count": booking.child_count,
            "baby_count": booking.baby_count,
            "total_price": total_price,
            "status": "pending",
            "created_at": new_booking[1]
        }
    
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig)
        # Check if it's the GiST exclusion constraint blocking the double booking
        if "prevent_double_booking" in error_msg:
            raise HTTPException(status_code=400, detail="Asset is already booked for these dates.")
        # Check if it's the valid_guest_count CHECK constraint
        elif "valid_guest_count" in error_msg:
             raise HTTPException(status_code=400, detail="Booking must have at least 1 adult or child.")
        else:
            raise HTTPException(status_code=400, detail="Database constraint violation.")
            
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")