from fastapi import APIRouter, HTTPException
from feature.tickets import buy_tickets
from feature.voting import create_vote_transaction
from db.schemas import TicketPurchase, VoteProposalCreate, VoteSubmit
from db.database import proposals_collection, get_next_proposal_id, charities_collection
from datetime import datetime

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
            "contact_email": charity.get("contact_email")
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


async def update_charity_status(charity: dict):
    """Check open/close window and update status dynamically"""
    now = datetime.utcnow()

    try:
        open_time = datetime.fromisoformat(charity["open_time"])
        close_time = datetime.fromisoformat(charity["close_time"])
    except Exception:
        return charity  # skip if invalid or missing times

    if not charity.get("session_consumed", False):
        if open_time <= now <= close_time:
            charity["status"] = "Open"
        elif now > close_time:
            charity["status"] = "Closed"
            charity["session_consumed"] = True
            await charities_collection.update_one(
                {"charity_id": charity["charity_id"]},
                {"$set": {"status": "Closed", "session_consumed": True}}
            )
    return charity


@vote_router.get("/active-proposals")
async def get_active_proposals():
    """Get proposals linked to currently open charities"""
    try:
        proposals = []
        async for proposal in proposals_collection.find({}, {"_id": 0}):
            charity = await charities_collection.find_one({"charity_id": proposal["charity"]["charity_id"]})
            if charity:
                charity = await update_charity_status(charity)
                if charity["status"] == "Open":
                    proposals.append(proposal)

        return {
            "success": True,
            "count": len(proposals),
            "proposals": proposals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposals: {e}")
