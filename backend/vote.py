# backend/vote.py
from http.client import HTTPException
from fastapi import APIRouter
from feature.tickets import buy_tickets
from feature.voting import create_vote_transaction, start_new_voting_period
from db.schemas import CreditPurchaseResponse, VoteProposalCreate, VoteSubmit
from db.database import proposals_collection, users_collection, get_next_proposal_id

vote_router = APIRouter(prefix="/vote", tags=["Vote"])
start_new_voting_period()

@vote_router.post("/buy-tickets", response_model=CreditPurchaseResponse)
def buy_credits_endpoint(request: CreditPurchaseResponse):
    return buy_tickets(request)

@vote_router.post("/create-proposal")
async def create_proposal_endpoint(request: VoteProposalCreate):

    # 🔢 Generate simple ID
    proposal_id = await get_next_proposal_id()

    # 🧱 Build the document
    proposal_data = {
        "proposal_id": proposal_id,
        "title": request.title,
        "description": request.description,
        "options": request.options,
        "votes": {opt: 0 for opt in request.options}
    }

    # 💾 Insert into MongoDB
    result = await proposals_collection.insert_one(proposal_data)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    # ✅ Return readable ID
    return {
        "success": True,
        "id": proposal_id,
        "message": f"Proposal '{request.title}' created successfully."
    }

    
@vote_router.post("/submit-vote")
async def submit_vote_endpoint(request: VoteSubmit):
    return await create_vote_transaction( 
        user_id=int(request.user_id),
        proposal_id=int(request.proposal_id),
        votes=request.votes
    )
