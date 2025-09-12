from fastapi import APIRouter, Form, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any

from .blockchain.blockchain import Blockchain, Transactions
from .db.database import get_database_collections, get_settings_collection

# Router setup
router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


# --- Endpoints ---

@router.get("/")
async def get_blockchain_data():
    # In a MongoDB-based system, you would retrieve blocks and transactions from the DB.
    # For now, we will assume an in-memory blockchain for validation and display purposes.
    # A full implementation would involve loading the entire chain from the database.
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="Invalid Blockchain")

    return {
        "valid": True,
        "pending_count": len(blockchain.pending_transactions),
        "pending_transactions": blockchain.pending_transactions,
        "chain": blockchain.chain,
    }


@router.get("/{index}")
async def get_single_block(index: int):
    if index < 0 or index >= len(blockchain.chain):
        raise HTTPException(status_code=404, detail="Block not found")
    return blockchain.chain[index]


@router.post("/mine_block/")
async def mine_block(miner: str = Form(...), collections: Dict[str, Any] = Depends(get_database_collections)):
    proposals_collection = collections["proposals_collection"]
    settings_collection = get_settings_collection()
    
    # Check if a voting session is in progress
    voting_status = await settings_collection.find_one({"_id": "voting_status"})
    if voting_status and voting_status.get("status") == "in_progress":
        raise HTTPException(status_code=400, detail="Cannot mine a new block while a voting session is active.")
        
    # Get all unconfirmed proposals from the database
    unconfirmed_proposals = await proposals_collection.find({"confirmed": False}).to_list(length=None)
    
    # If there are no unconfirmed proposals, there's nothing to mine
    if not unconfirmed_proposals:
        raise HTTPException(status_code=400, detail="No unconfirmed proposals to mine.")
    
    # Create the block with the unconfirmed proposals
    block = blockchain.mine_block(data=unconfirmed_proposals, miner=miner)
    
    # Update the status of the proposals to confirmed
    for proposal in unconfirmed_proposals:
        await proposals_collection.update_one(
            {"_id": proposal["_id"]},
            {"$set": {"confirmed": True}}
        )

    return {"message": f"Block mined by {miner}!", "block": block}


@router.get("/pending_transactions")
async def get_pending_transactions(collections: Dict[str, Any] = Depends(get_database_collections)):
    votes_collection = collections["votes_collection"]
    pending_transactions = await votes_collection.find().to_list(length=None)
    
    return {
        "pending_transactions": pending_transactions,
        "count": len(pending_transactions),
    }


@router.get("/balance/{user}")
async def get_balance(user: str, collections: Dict[str, Any] = Depends(get_database_collections)):
    users_collection = collections["users_collection"]
    user_data = await users_collection.find_one({"username": user})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"user": user, "balance": user_data.get("credit_balance", 0)}
