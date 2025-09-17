# backend/vote.py
from fastapi import APIRouter, HTTPException

from db.database import charities_collection, get_next_charity_id
from db.schemas import CharityCreate, CharityResponseModel

charity_router = APIRouter(prefix="/charities", tags=["Charities"])

@charity_router.post("/add-charity")
async def add_charity(request: CharityCreate):
    charity_id = await get_next_charity_id()
    if charity_id:
        result = await charities_collection.insert_one(request.dict())
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create charity")
    # Build the document
    charity_data = {
        "charity_id": charity_id,
        "description": request.description,
        "email": request.contact_email,
    }
    result = await charities_collection.insert_one(charity_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create charity")

    
    # Build the document
    charity_data = {
        "charity_id": charity_id,
        "description": request.description,
        "email": request.contact_email,
    }
    
    return {
        "success": True,
        "id": charity_id,
        "message": f"Charity '{request.name}' created successfully."
    }

    