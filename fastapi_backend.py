"""
FastAPI Backend for Car Service Booking System
This server manages slots data and provides REST API endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import random
import string
from datetime import datetime

app = FastAPI(title="Car Service Booking API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo slots data
demo_slots = [
    # Today (2025-12-31)
    {"date": "2025-12-31", "time": "09:00 AM", "available": False},
    {"date": "2025-12-31", "time": "11:00 AM", "available": True},
    {"date": "2025-12-31", "time": "01:00 PM", "available": False},
    {"date": "2025-12-31", "time": "03:00 PM", "available": True},
    {"date": "2025-12-31", "time": "05:00 PM", "available": True},

    # Tomorrow (2026-01-01)
    {"date": "2026-01-01", "time": "09:00 AM", "available": True},
    {"date": "2026-01-01", "time": "11:00 AM", "available": True},
    {"date": "2026-01-01", "time": "01:00 PM", "available": False},
    {"date": "2026-01-01", "time": "03:00 PM", "available": True},
    {"date": "2026-01-01", "time": "05:00 PM", "available": True},

    # Day after tomorrow (2026-01-02)
    {"date": "2026-01-02", "time": "09:00 AM", "available": True},
    {"date": "2026-01-02", "time": "11:00 AM", "available": True},
    {"date": "2026-01-02", "time": "01:00 PM", "available": True},
    {"date": "2026-01-02", "time": "03:00 PM", "available": True},
    {"date": "2026-01-02", "time": "05:00 PM", "available": True},
]


# Pydantic models
class BookingRequest(BaseModel):
    customer_name: str
    phone: str
    car_model: str
    service_type: str
    date: str
    time: str


class BookingResponse(BaseModel):
    success: bool
    ticket_id: str
    customer_name: str
    phone: str
    car_model: str
    service_type: str
    date: str
    time: str
    message: str


class SlotsResponse(BaseModel):
    success: bool
    total_slots: int
    slots: List[dict]


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Car Service Booking API",
        "version": "1.0.0"
    }


@app.get("/api/slots", response_model=SlotsResponse, tags=["Slots"])
async def get_available_slots(date: Optional[str] = None):
    """
    Get available car service slots

    Args:
        date: Optional date filter in YYYY-MM-DD format (e.g., '2025-12-31')

    Returns:
        JSON object with success status, total count, and array of available slots
    """
    # Get current date and time
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%I:%M %p")

    print(f"[FastAPI] get_available_slots called - Current time: {current_date} {current_time}")

    # Filter available slots
    slots = [s for s in demo_slots if s["available"]]
    print(f"[FastAPI] Available slots before time filter: {len(slots)}")

    # Filter out past time slots for today
    filtered_slots = []
    for slot in slots:
        if slot["date"] == current_date:
            # Parse slot time and current time for comparison
            slot_time = datetime.strptime(slot["time"], "%I:%M %p")
            now_time = datetime.strptime(current_time, "%I:%M %p")

            # Only include future time slots for today
            if slot_time.time() > now_time.time():
                filtered_slots.append(slot)
        else:
            # Include all slots for future dates
            filtered_slots.append(slot)

    slots = filtered_slots
    print(f"[FastAPI] Slots after time filter: {len(slots)}")

    # Apply date filter if provided
    if date:
        slots = [s for s in slots if s["date"] == date]
        print(f"[FastAPI] Slots after date filter ({date}): {len(slots)}")

    print(f"[FastAPI] Returning {len(slots)} slots")

    return {
        "success": True,
        "total_slots": len(slots),
        "slots": slots
    }


@app.post("/api/book", response_model=BookingResponse, tags=["Booking"])
async def book_car_service(booking: BookingRequest):
    """
    Book a car service appointment

    Args:
        booking: BookingRequest object with customer details and slot information

    Returns:
        Booking confirmation with ticket ID and details

    Raises:
        HTTPException: If the requested slot is not available
    """
    date = booking.date
    time = booking.time

    print(f"[FastAPI] Booking request for {date} at {time}")

    # Find slot
    slot_found = False
    for slot in demo_slots:
        if slot["date"] == date and slot["time"] == time and slot["available"]:
            slot["available"] = False
            slot_found = True
            print(f"[FastAPI] Slot marked as booked: {date} {time}")
            break

    if not slot_found:
        print(f"[FastAPI] Slot not available: {date} {time}")
        raise HTTPException(
            status_code=400,
            detail=f"Slot not available for {date} at {time}"
        )

    # Generate ticket ID
    ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    print(f"[FastAPI] Booking confirmed! Ticket ID: {ticket_id}")

    return {
        "success": True,
        "ticket_id": ticket_id,
        "customer_name": booking.customer_name,
        "phone": booking.phone,
        "car_model": booking.car_model,
        "service_type": booking.service_type,
        "date": date,
        "time": time,
        "message": f"Booking confirmed! Ticket: {ticket_id}"
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚗 Car Service Booking FastAPI Server")
    print("=" * 60)
    print("Server URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
