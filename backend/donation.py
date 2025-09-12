from fastapi import APIRouter, HTTPException
from feature.donate import create_donation
from db.schemas import DonationCreate, DonationResponse

donation_router = APIRouter(prefix="/donate", tags=["Donate"])

@donation_router.post("/", response_model=DonationResponse)
async def donate(donation: DonationCreate):    
    result = await create_donation(donation)
    if not result:
        raise HTTPException(status_code=400, detail="Donation failed.")
    return result   