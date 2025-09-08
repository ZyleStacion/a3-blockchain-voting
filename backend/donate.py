from fastapi import APIRouter
from db.schemas import DonationCreate, DonationResponse
from feature.donations import process_donations

donate_router = APIRouter(prefix="/donate", tags=["Donate"])

@donate_router.post("/make-donation")
def donate(input: DonationCreate) -> DonationResponse:
    return process_donations(input)