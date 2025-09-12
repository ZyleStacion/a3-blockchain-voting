# backend/vote.py
from fastapi import APIRouter, HTTPException
from .feature.tickets import buy_tickets
from .feature.Voting import create_vote_transaction
from .db.schemas import TicketPurchase, CreditPurchaseResponse, VoteProposalCreate, VoteSubmit
from .db.database import proposals_collection, get_next_proposal_id, users_collection

vote_router = APIRouter(prefix="/vote", tags=["Vote"])


@vote_router.post("/buy-tickets")
async def buy_tickets_endpoint(request: TicketPurchase):
    result = await buy_tickets(request)

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result["message"])

    return result

    
@vote_router.post("/create-proposal")
async def create_proposal_endpoint(request: VoteProposalCreate):
    proposal_id = await get_next_proposal_id()

    # Build the document
    proposal_data = {
        "_id": proposal_id,
        "title": request.title,
        "description": request.description,
        "options": request.options,
        "votes": {opt: 0 for opt in request.options}
    }

    # Insert into MongoDB
    result = await proposals_collection.insert_one(proposal_data)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    # Return readable ID
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