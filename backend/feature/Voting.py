from typing import Dict, Any, List
import uuid
from db.database import proposals_collection, users_collection, get_settings_collection
from blockchain.blockchain import Blockchain, Transactions
import json
import time
import hashlib

THRESHOLD_AMOUNT = 1000
VOTING_PERIOD_SECONDS = 300

# Initialize global blockchain instance
blockchain = Blockchain()

def calculate_hash(data_dict: Dict[str, Any]) -> str:
    block_string = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

async def create_vote_transaction(user_id: str, proposal_id: str, tickets: int):
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        return {"success": False, "message": f"User ID {user_id} not found."}
    
    if user.get("voting_tickets", 0) < tickets:
        return {"success": False, "message": "Not enough voting tickets."}

    proposal = await proposals_collection.find_one({"_id": proposal_id})
    if not proposal:
        return {"success": False, "message": f"Proposal ID {proposal_id} not found."}

    await users_collection.update_one(
        {"_id": user_id},
        {"$inc": {"voting_tickets": -tickets}}
    )
    
    return record_vote_on_chain(
        voter_pubkey=user.get("public_key", str(user_id)),
        proposal_id=proposal_id,
        tickets=tickets
    )

def record_vote_on_chain(voter_pubkey: str, proposal_id: str, tickets: int) -> dict:
    tx_id = f"vote_{uuid.uuid4().hex[:10]}"
    
    tx = Transactions(
        transaction_id=tx_id,
        sender=voter_pubkey,
        receiver=proposal_id,
        amount=tickets
    )

    success = blockchain.insert_transaction(tx)
    if not success:
        return {"success": False, "message": "Failed to insert vote transaction."}

    block = blockchain.mine_block(data="Vote Block", miner="SYSTEM")
    blockchain.save_chain()

    return {
        "success": True,
        "message": f"Vote recorded: {voter_pubkey} voted {tickets} tickets on {proposal_id}",
        "tx_id": tx_id,
        "block_index": block["index"],
        "block_hash": block["hash"]
    }

# --- Logic for using MongoDB ---

async def start_new_voting_period():
    settings_collection = get_settings_collection()
    # update vote status on mongoDB and record time
    await settings_collection.update_one(
        {"_id": "voting_status"},
        {"$set": {"is_voting_active": True, "voting_period_start_time": time.time()}},
        upsert=True
    )
    # Donation pot is checked on ticket purchase, might not be needed here.
    print("Pot has reached overflow threshold. Initiating vote.")
    return {"message": "New voting period has started."}


async def finalize_voting():
    print("\nFinalizing voting period...")
    
    # 1. fetch all temporary transactions
    current_transactions = blockchain.pending_transactions
    if not current_transactions:
        print("No transactions to finalize.")
        
    # 2. generate block and create chain
    new_block = blockchain.mine_block(data="Final Vote Block", miner="SYSTEM")
    blockchain.save_chain()
    
    # 3. finalize voting result
    vote_counts = {}
    for tx in current_transactions:
        prop_id = tx.receiver
        tickets_cast = tx.amount
        vote_counts[prop_id] = vote_counts.get(prop_id, 0) + tickets_cast
    
    if vote_counts:
        winner_id = max(vote_counts, key=vote_counts.get)
        settings_collection = get_settings_collection()
        voting_status = await settings_collection.find_one({"_id": "voting_status"})
        donation_amount = voting_status.get("donation_pot", 0)

        # 4. Show result and reset donation status
        print(f"\n[Result] The winner of the vote is '{winner_id}'. A total of {donation_amount}$ will be donated.")
        
        await settings_collection.update_one(
            {"_id": "voting_status"},
            {"$set": {"donation_pot": 0}}
        )
    
    # 5. Reset voting session status (is_voting_active to False로)
    settings_collection = get_settings_collection()
    await settings_collection.update_one(
        {"_id": "voting_status"},
        {"$set": {"is_voting_active": False, "voting_period_start_time": None}}
    )
    
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