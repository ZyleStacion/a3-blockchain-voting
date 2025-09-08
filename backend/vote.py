# backend/vote.py
from http.client import HTTPException
from fastapi import APIRouter
from feature.tickets import buy_tickets
from feature.voting import create_vote_transaction, start_new_voting_period
from db.schemas import CreditPurchaseResponse, VoteProposalCreate, VoteSubmit
from db.database import proposals_collection

vote_router = APIRouter(prefix="/vote", tags=["Vote"])
start_new_voting_period()

@vote_router.post("/buy-tickets", response_model=CreditPurchaseResponse)
def buy_credits_endpoint(request: CreditPurchaseResponse):
    return buy_tickets(request)

@vote_router.post("/create-proposal")
async def create_proposal_endpoint(request: VoteProposalCreate):
    proposal_data = {
        "title": request.title,
        "description": request.description,
        "options": request.options,
        "votes": {opt: 0 for opt in request.options}  # ⬅️ initialize vote counts
    }

    result = await proposals_collection.insert_one(proposal_data)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    return {
        "success": True,
        "id": str(result.inserted_id),
        "message": f"Proposal '{request.title}' created successfully."
    }
@vote_router.post("/submit-vote")
def submit_vote_endpoint(request: VoteSubmit):
    return create_vote_transaction(
        request.user_id,      
        request.proposal_id,
        request.votes
    )