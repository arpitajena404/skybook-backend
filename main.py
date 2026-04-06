from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import flights, bookings

app = FastAPI(title="Flight Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights.router,  prefix="/flights",  tags=["Flights"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

@app.get("/")
def root():
    return {"message": "Flight Booking API is running!"}