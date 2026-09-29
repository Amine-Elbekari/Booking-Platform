from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from database import get_db, get_redis
from redis.asyncio import Redis
from schemas.booking import BookingCreate
from dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db),  redis: Redis = Depends(get_redis), current_user: User = Depends(get_current_user)):
    
    if str(booking.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only create bookings for your own account.")
    
    delta = booking.end_date - booking.start_date
    total_days = delta.days # days property from timedelta object generated under the hood by python

    if total_days <= 0:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    lock_key = f"booking_lock: {booking.asset_id}"
    
    # Try to acquire the lock: SET (key) (value) NX (only if doesn't exist) EX (expire in 60s)
    lock_acquired = await redis.set(lock_key, "locked", nx=True, ex=60)

    if not lock_acquired:
        # if someone else holds the lock, fail immediately so no DB query needed
        raise HTTPException(status_code=409, detail="This asset is currently being booked by someone else.")
    try:

        # clean up stale rows using the schema's pending and cancelled
        cleanup_query = text("""
            UPDATE bookings
            SET status = 'expired'
            WHERE asset_id = :asset_id
                AND status = 'pending_payment'
                AND created_at < NOW() - INTERVAL '60 seconds'
        """)
        await db.execute(cleanup_query, {'asset_id': str(booking.asset_id)})
        
        # the overlap check using the schema's pending
        overlap_query = text("""
            SELECT id FROM bookings WHERE asset_id = :asset_id
                AND booking_dates && daterange(:start_date, :end_date, '[)')
                AND status IN ('confirmed', 'pending_payment')
            FOR UPDATE
        """)
        overlap_result = await db.execute(overlap_query, {
            "asset_id": str(booking.asset_id),
            "start_date": booking.start_date,
            "end_date": booking.end_date
        })

        if overlap_result.fetchone():
            await db.rollback()
            await redis.delete(lock_key)
            raise HTTPException(status_code=409, detail="Asset is already booked for these dates.")

        # GET asset price 
        price_query = text("""
            SELECT price_per_night
            FROM assets
            WHERE id = :asset_id
        """)
        result = await db.execute(price_query, {"asset_id": str(booking.asset_id)})
        asset = result.fetchone()

        if not asset:
            await db.rollback()
            await redis.delete(lock_key)
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
                :adult_count, :child_count, :baby_count, 'pending_payment'
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
        # explicitly delete lock upon success
        await redis.delete(lock_key)

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
            "status": "pending_payment",
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
        await redis.delete(lock_key)
        raise
    except Exception as e:
        await db.rollback()
        await redis.delete(lock_key)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")