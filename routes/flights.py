from fastapi import APIRouter, HTTPException
from database import get_connection

router = APIRouter()

# 1. Search flights by source and destination city
@router.get("/search")
def search_flights(source_city: str, destination_city: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            f.f_id,
            f.flight_name,
            f.airline,
            src.city   AS source_city,
            src.name   AS source_airport,
            dst.city   AS destination_city,
            dst.name   AS destination_airport,
            f.dept_time,
            f.arrival_time,
            f.eco_price,
            f.business_price,
            f.first_price
        FROM FLIGHT f
        JOIN AIRPORT src ON f.source_id      = src.airport_id
        JOIN AIRPORT dst ON f.destination_id = dst.airport_id
        WHERE LOWER(src.city) = LOWER(%s)
          AND LOWER(dst.city) = LOWER(%s)
        ORDER BY f.dept_time
    """
    cursor.execute(query, (source_city, destination_city))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        raise HTTPException(status_code=404, detail="No flights found for this route")
    return {"flights": results}


# 2. Get all airports (for frontend dropdowns)
@router.get("/airports")
def get_airports():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM AIRPORT ORDER BY country, city")
    airports = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"airports": airports}


# 3. Get a single flight by ID
@router.get("/{f_id}")
def get_flight(f_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            f.*,
            src.city AS source_city,
            src.name AS source_airport,
            dst.city AS destination_city,
            dst.name AS destination_airport
        FROM FLIGHT f
        JOIN AIRPORT src ON f.source_id      = src.airport_id
        JOIN AIRPORT dst ON f.destination_id = dst.airport_id
        WHERE f.f_id = %s
    """
    cursor.execute(query, (f_id,))
    flight = cursor.fetchone()
    cursor.close()
    conn.close()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"flight": flight}