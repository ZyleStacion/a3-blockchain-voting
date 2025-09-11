# backend/vote.py

from fastapi import APIRouter, HTTPException
from feature.tickets import buy_tickets
from feature.voting import create_vote_transaction
from db.schemas import TicketPurchase, CreditPurchaseResponse, VoteProposalCreate, VoteSubmit
from db.database import proposals_collection, users_collection, get_next_proposal_id

vote_router = APIRouter(prefix="/vote", tags=["Vote"])

# ❌ The call to start_new_voting_period() should not be at the top level.
# It should be triggered by an event, such as the donation pot reaching the threshold.
# We will rely on the logic in buy_tickets.py to handle this.

@vote_router.post("/buy-tickets", response_model=CreditPurchaseResponse)
async def buy_tickets_endpoint(request: TicketPurchase):
    return await buy_tickets(request)

@vote_router.post("/create-proposal")
async def create_proposal_endpoint(request: VoteProposalCreate):
    # 🔢 Generate simple ID
    proposal_id = await get_next_proposal_id()

    # 🧱 Build the document
    proposal_data = {
        "_id": proposal_id,
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
    # Pass the 'tickets' field from the request body
    return await create_vote_transaction(
        user_id=request.user_id,
        proposal_id=request.proposal_id,
        tickets=request.tickets
    )

@vote_router.get("/active-proposals")
async def get_active_proposals():
    """Get all active voting proposals"""
    try:
        proposals = await proposals_collection.find({}).to_list(100)
        return proposals
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch proposals")

@vote_router.get("/proposal/{proposal_id}")
async def get_proposal(proposal_id: int):
    """Get a specific proposal by ID"""
    try:
        proposal = await proposals_collection.find_one({"_id": proposal_id})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        return proposal
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch proposal")