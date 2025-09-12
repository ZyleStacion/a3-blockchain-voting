from db.database import donation_collection, users_collection, get_next_donation_id
from db.schemas import DonationCreate, DonationResponse


async def create_donation(donation: DonationCreate):    
    user = await users_collection.find_one({"user_id": donation.user_id})

    if not user:
        return {"success": False, "message": f"User ID {donation.user_id} not found."}

    if user.get("donation_balance", 0) < donation.amount:
        return {"success": False, "message": "Not enough funds."}
    
    await users_collection.update_one(
        {"user_id": donation.user_id},
        {"$inc": {"donation_balance": -donation.amount}}
    )

    donation_id = await get_next_donation_id()
    
    donation_doc = {
        "donation_id": donation_id,
        "user_id": donation.user_id,
        "amount": donation.amount,
        "message": donation.message
    }
    
    results = await donation_collection.insert_one(donation_doc)
    new_donation = await donation_collection.find_one({"_id": results.inserted_id})
    
    return DonationResponse(
        donation_id=new_donation["donation_id"],
        user_id=new_donation["user_id"],
        amount=new_donation["amount"],
        message="Donation recorded successfully"
    )