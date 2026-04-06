from fastapi import APIRouter, HTTPException
from database import get_connection
from pydantic import BaseModel

router = APIRouter()

class BookingRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    nationality: str
    age: int
    f_id: int
    flight_class: str
    meal_preference: str

@router.post("/create")
def create_booking(data: BookingRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Step 1 — Check if user with this email already exists
    cursor.execute("SELECT user_id FROM USER WHERE email = %s", (data.email,))
    existing = cursor.fetchone()

    if existing:
        user_id = existing["user_id"]
    else:
        # Step 2 — Insert new user
        cursor.execute("""
            INSERT INTO USER (first_name, last_name, email, phone, password, nationality, age)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data.first_name, data.last_name, data.email, data.phone, "default123", data.nationality, data.age))
        conn.commit()
        user_id = cursor.lastrowid

    # Step 3 — Fetch flight price
    cursor.execute("SELECT eco_price, business_price, first_price FROM FLIGHT WHERE f_id = %s", (data.f_id,))
    flight = cursor.fetchone()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    price_map = {
        "Economy":  flight["eco_price"],
        "Business": flight["business_price"],
        "First":    flight["first_price"]
    }

    if data.flight_class not in price_map:
        raise HTTPException(status_code=400, detail="Invalid class")

    amount = price_map[data.flight_class]

    # Step 4 — Insert booking
    cursor.execute("""
        INSERT INTO BOOKING (user_id, f_id, class, meal_preference, amount)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, data.f_id, data.flight_class, data.meal_preference, amount))

    conn.commit()
    booking_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return {
        "message": "Booking successful!",
        "booking_id": booking_id,
        "user_id": user_id,
        "amount_charged": amount
    }


@router.get("/user/{user_id}")
def get_user_bookings(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            b.booking_id, b.class, b.meal_preference, b.amount,
            f.flight_name, f.airline,
            src.city AS source_city,
            dst.city AS destination_city,
            f.dept_time, f.arrival_time
        FROM BOOKING b
        JOIN FLIGHT f ON b.f_id = f.f_id
        JOIN AIRPORT src ON f.source_id  = src.airport_id
        JOIN AIRPORT dst ON f.destination_id = dst.airport_id
        WHERE b.user_id = %s
        ORDER BY b.booking_id DESC
    """
    cursor.execute(query, (user_id,))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"bookings": bookings}