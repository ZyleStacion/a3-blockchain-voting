from typing import Dict, Any, List
import uuid
import time
import json
import hashlib
from db.database import proposals_collection, users_collection, votes_collection, get_settings_collection
from blockchain.blockchain import Blockchain, Transactions

# -- Initialize global settings --
THRESHOLD_AMOUNT = 1000
VOTING_PERIOD_SECONDS = 300
blockchain = Blockchain()

def calculate_hash(data_dict: Dict[str, Any]) -> str:
    block_string = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

# -- Core vote functions --
async def create_vote_transaction(user_id: int, proposal_id: int, tickets: int):
    # 1. Validate user and proposal existence
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        return {"success": False, "message": f"User ID {user_id} not found."}
    
    if user.get("voting_tickets", 0) < tickets:
        return {"success": False, "message": "Not enough voting tickets."}

    proposal = await proposals_collection.find_one({"_id": proposal_id})
    if not proposal:
        return {"success": False, "message": f"Proposal ID {proposal_id} not found."}

    # 2. Deduct user tickets (MongoDB)
    await users_collection.update_one(
        {"_id": user_id},
        {"$inc": {"voting_tickets": -tickets}}
    )

    # 3. Record vote (Added into MongoDB votes)
    vote_doc = {
        "user_id": user_id,
        "proposal_id": proposal_id,
        "tickets_used": tickets,
        "timestamp": time.time()  # Timestamps for tiebreaker
    }
    await votes_collection.insert_one(vote_doc)

    # 4. Record transactions onto chain (record_vote_on_chain)
    voter_pubkey = user.get("public_key", str(user_id))
    tx_id = f"vote_{uuid.uuid4().hex[:10]}"
    tx = Transactions(
        transaction_id=tx_id,
        sender=voter_pubkey,
        receiver=proposal_id,
        amount=tickets,
        timestamp=time.time()
    )
    success = blockchain.insert_transaction(tx)
    if not success:
        return {"success": False, "message": "Failed to insert vote transaction on blockchain."}

    return {
        "success": True,
        "message": f"Vote recorded for proposal {proposal_id}",
        "user_id": user_id,
        "proposal_id": proposal_id,
        "tickets_used": tickets
    }

# -- Manages vote session --
async def start_new_voting_period():
    settings_collection = get_settings_collection()
    await settings_collection.update_one(
        {"_id": "voting_status"},
        {"$set": {"is_voting_active": True, "voting_period_start_time": time.time()}},
        upsert=True
    )
    print("Pot has reached overflow threshold. Initiating vote.")
    return {"message": "New voting period has started."}

async def finalize_voting():
    print("\nFinalizing voting period...")
    
    # 1. Fetches all votes from MongoDB
    # TODO : Add query to fetch all
    # Ex: votes_collection.find({"timestamp": {"$gte": voting_period_start_time}})
    current_votes = await votes_collection.find({}).to_list(length=None) 
    
    if not current_votes:
        print("No transactions to finalize.")
        
    vote_counts = {}
    first_vote_timestamps = {}
    
    for vote in current_votes:
        prop_id = vote["proposal_id"]
        tickets_cast = vote["tickets_used"]
        
        vote_counts[prop_id] = vote_counts.get(prop_id, 0) + tickets_cast
        
        if prop_id not in first_vote_timestamps:
            first_vote_timestamps[prop_id] = vote["timestamp"]
    
    # 2. Result confirm and tiebreaker
    if vote_counts:
        max_tickets = max(vote_counts.values())
        tied_proposals = [
            prop_id for prop_id, count in vote_counts.items() 
            if count == max_tickets
        ]
        
        if len(tied_proposals) == 1:
            winner_id = tied_proposals[0]
        else:
            winner_id = min(tied_proposals, key=lambda prop: first_vote_timestamps[prop])
            
        settings_collection = get_settings_collection()
        voting_status = await settings_collection.find_one({"_id": "voting_status"})
        donation_amount = voting_status.get("donation_pot", 0)

        print(f"\n[Result] The winner of the vote is '{winner_id}'. A total of {donation_amount}$ will be donated.")
        
        await settings_collection.update_one(
            {"_id": "voting_status"},
            {"$set": {"donation_pot": 0}}
        )
    
    # 3. Generate Blockchain and initialize
    new_block = blockchain.mine_block(data="Final Vote Block", miner="SYSTEM")
    blockchain.save_chain()
    
    settings_collection = get_settings_collection()
    await settings_collection.update_one(
        {"_id": "voting_status"},
        {"$set": {"is_voting_active": False, "voting_period_start_time": None}}
    )
    
    # (optional) Delete vote history from MongoDB
    await votes_collection.delete_many({})

    print("Votes were concluded and blocks were created.")
    return {"message": "Voting finalized and results recorded."}

async def check_and_finalize_voting_job():
    settings_collection = get_settings_collection()
    voting_status = await settings_collection.find_one({"_id": "voting_status"})
    
    if voting_status and voting_status.get("is_voting_active"):
        start_time = voting_status.get("voting_period_start_time")
        if start_time and (time.time() - start_time) >= VOTING_PERIOD_SECONDS:
            print("\nVoting period has ended. Finalizing votes...")
            await finalize_voting()