# backend/vote.py
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from db.database import charities_collection, get_next_charity_id
from db.schemas import CharityCreate, CharityResponseModel, CharityUpdate

charity_router = APIRouter(prefix="/charities", tags=["Charities"])

# --- Create a new charity ---
@charity_router.post("/add-charity")
async def add_charity(request: CharityCreate):
    charity_id = await get_next_charity_id()

    charity_data = {
        "charity_id": charity_id,
        "name": request.name,
        "description": request.description,
        "contact_email": request.contact_email,
        "status": "Closed",                 # Default closed until open_time
        "open_time": request.open_time,     # ISO string
        "close_time": request.close_time,   # ISO string
        "session_consumed": False
    }

    result = await charities_collection.insert_one(charity_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create charity")

    return {
        "success": True,
        "id": charity_id,
        "message": f"Charity '{request.name}' created successfully."
    }


@charity_router.get("/get-all")
async def get_all_charities():
    charities = []
    async for charity in charities_collection.find():
        charities.append(CharityResponseModel(
            id=charity.get("charity_id"),
            name=charity.get("name"),
            description=charity.get("description"),
            contact_email=charity.get("contact_email"),
            open_time=charity.get("open_time"),
            close_time=charity.get("close_time"),
            status=charity.get("status")
        ))
    return {"charities": charities}

# --- Utility: update status based on current time ---
async def update_charity_status(charity: dict):
    now = datetime.utcnow()
    try:
        open_time = datetime.fromisoformat(charity["open_time"])
        close_time = datetime.fromisoformat(charity["close_time"])
    except Exception:
        return charity  # skip if invalid or missing times

    if not charity.get("session_consumed", False):
        if open_time <= now <= close_time:
            charity["status"] = "Open"
        elif now > close_time:
            charity["status"] = "Closed"
            charity["session_consumed"] = True
            # persist closed state
            await charities_collection.update_one(
                {"charity_id": charity["charity_id"]},
                {"$set": {"status": "Closed", "session_consumed": True}}
            )
    return charity


# --- Get only active (open) charities ---
@charity_router.get("/get-active")
async def get_active_charities():
    charities = []
    async for charity in charities_collection.find():
        charity = await update_charity_status(charity)
        if charity["status"] == "Open":
            charities.append(CharityResponseModel(
                id=charity.get("charity_id"),
                name=charity.get("name"),
                description=charity.get("description"),
                contact_email=charity.get("contact_email"),
                open_time=charity.get("open_time"),
                close_time=charity.get("close_time"),
                status=charity.get("status")
            ))
    return {"charities": charities}


# --- Update open/close times (for testing) ---
@charity_router.put("/update-session/{charity_id}")
async def update_session_times(charity_id: int, request: CharityUpdate = Body(...)):
    update_data = {}
    if request.open_time:
        update_data["open_time"] = request.open_time
        update_data["status"] = "Closed"  # reset until new open_time
    if request.close_time:
        update_data["close_time"] = request.close_time

    # Reset session for testing
    update_data["session_consumed"] = False

    result = await charities_collection.update_one(
        {"charity_id": charity_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Charity not found")

    return {"success": True, "message": "Charity session updated successfully"}