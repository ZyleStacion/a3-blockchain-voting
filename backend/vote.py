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

    # 1) Normalize charity_id (allow int or str in DB)
    charity = await charities_collection.find_one({"charity_id": request.charity_id})
    if not charity:
        charity = await charities_collection.find_one({"charity_id": str(request.charity_id)})

    if not charity:
        raise HTTPException(
            status_code=404,
            detail=f"Charity ID {request.charity_id} not found"
        )

    # 2) Build the proposal document (always embed charity)
    proposal_data = {
        "proposal_id": int(proposal_id),
        "title": request.title,
        "description": request.description,
        "yes_counter": 0,
        "charity": {
            "charity_id": charity["charity_id"],
            "name": charity["name"],
            "contact_email": charity.get("contact_email", None),
        },
        "created_at": datetime.utcnow()
    }

    # 3) Insert into MongoDB
    result = await proposals_collection.insert_one(proposal_data)
    if not result.inserted_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to create proposal"
        )

    # 4) Response payload
    return {
        "success": True,
        "id": proposal_id,
        "title": request.title,
        "charity": charity["name"],
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
        print("🔍 Fetching active proposals...")
        
        # Get all proposals first
        proposals_cursor = proposals_collection.find({}, {"_id": 0})
        all_proposals = await proposals_cursor.to_list(length=None)
        
        print(f"📄 Found {len(all_proposals)} total proposals")
        
        active_proposals = []
        
        for proposal in all_proposals:
            try:
                charity_id = proposal.get("charity", {}).get("charity_id")
                if charity_id:
                    charity = await charities_collection.find_one({"charity_id": charity_id})
                    if charity:
                        charity = await update_charity_status(charity)
                        if charity.get("status") == "Open":
                            active_proposals.append(proposal)
                            print(f"✅ Added active proposal: {proposal.get('title', 'N/A')}")
            except Exception as e:
                print(f"❌ Error processing proposal {proposal.get('proposal_id', 'N/A')}: {e}")
                continue
        
        print(f"🎯 Returning {len(active_proposals)} active proposals")
        
        return {
            "success": True,
            "count": len(active_proposals),
            "proposals": active_proposals
        }
        
    except Exception as e:
        print(f"❌ Error in get_active_proposals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposals: {str(e)}")