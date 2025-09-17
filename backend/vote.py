# backend/vote.py
from fastapi import APIRouter, HTTPException
from feature.tickets import buy_tickets
from feature.voting import create_vote_transaction
from db.schemas import TicketPurchase, VoteProposalCreate, VoteSubmit
from db.database import proposals_collection, get_next_proposal_id, charities_collection

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

    # 1) Check if charity exists
    charity = await charities_collection.find_one({"charity_id": request.charity_id})
    if not charity:
        raise HTTPException(status_code=404, detail=f"Charity ID {request.charity_id} not found")

    # 2) Build the proposal document
    proposal_data = {
        "proposal_id": proposal_id,
        "title": request.title,
        "description": request.description,
        "yes_counter": 0,
        "charity": {   # ✅ embed charity reference
            "charity_id": charity["charity_id"],
            "name": charity["name"],
            "email": charity["email"]
        }
    }

    # 3) Insert into MongoDB
    result = await proposals_collection.insert_one(proposal_data)

    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    return {
        "success": True,
        "id": proposal_id,
        "message": f"Proposal '{request.title}' created successfully for charity '{charity['name']}'."
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
        # Exclude `_id` so results are JSON-serializable
        cursor = proposals_collection.find({}, {"_id": 0})
        proposals = await cursor.to_list(length=None)  # None = fetch everything
        return {
            "success": True,
            "count": len(proposals),
            "proposals": proposals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposals: {e}")
