# backend/vote.py
from fastapi import APIRouter, HTTPException

from db.database import charities_collection, get_next_charity_id
from db.schemas import CharityCreate, CharityResponseModel

charity_router = APIRouter(prefix="/charities", tags=["Charities"])

@charity_router.post("/add-charity")
async def add_charity(request: CharityCreate):
    charity_id = await get_next_charity_id()
    
    # Build the document
    charity_data = {
        "charity_id": charity_id,
        "name": request.name,
        "description": request.description,
        "email": request.contact_email,
    }       
    
    # Insert into MongoDB
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
            contact_email=charity.get("contact_email")
        ))
    return {"charities": charities}