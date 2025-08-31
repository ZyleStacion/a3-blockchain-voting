from fastapi import APIRouter, HTTPException
from db.database import votes_collection
from db.schemas import VoteCreate, VoteResponse
from utils.DigitalSignature import verifying_vote

vote_router = APIRouter(prefix="/votes", tags=["Votes"])

@vote_router.post("/", response_model=VoteResponse)
async def cast_vote(vote: VoteCreate):
    vote_data = f"{vote.user_id}:{vote.charity_id}:{vote.tickets}"
    is_valid = await verifying_vote(vote.user_id, vote_data, vote.signature)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")

    result = await votes_collection.insert_one(vote.dict())
    saved_vote = await votes_collection.find_one({"_id": result.inserted_id})

    return {
        "id": str(saved_vote["_id"]),
        "user_id": saved_vote["user_id"],
        "charity_id": saved_vote["charity_id"],
        "tickets": saved_vote["tickets"],
        "signature": saved_vote["signature"]
    }
