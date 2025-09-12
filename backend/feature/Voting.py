from typing import Dict, Any, List
import uuid
from db.database import proposals_collection, users_collection, votes_collection
from blockchain.blockchain import Blockchain, Transactions
import json
import time
import hashlib

# These will now be handled by MongoDB logic.
# from db.save import load_data, save_data, load_chain_data, save_chain_data

THRESHOLD_AMOUNT = 1000
VOTING_PERIOD_SECONDS = 300

# Initialize global blockchain instance
blockchain = Blockchain()

def calculate_hash(data_dict: Dict[str, Any]) -> str:
    block_string = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

async def create_vote_transaction(user_id: int, proposal_id: int, tickets: int):
    # 1. Verify user exists and has enough tickets
    user = await users_collection.find_one({"user_id": int(user_id)})
    if not user:
        return {"success": False, "message": f"User ID {user_id} not found."}

    if user.get("voting_tickets", 0) < tickets:
        return {"success": False, "message": "Not enough tickets to vote."}

    # 2. Verify proposal exists
    proposal = await proposals_collection.find_one({"proposal_id": int(proposal_id)})
    if not proposal:
        return {"success": False, "message": f"Proposal ID {proposal_id} not found."}

    # 3. Decrement user's tickets
    await users_collection.update_one(
        {"user_id": int(user_id)},
        {"$inc": {"voting_tickets": -tickets}}
    )

    # 4. Record vote (for now: store in Mongo instead of blockchain)
    vote_doc = {
        "user_id": user_id,
        "proposal_id": proposal_id,
        "tickets_used": tickets
    }
    result = await votes_collection.insert_one(vote_doc)

    if not result.inserted_id:
        return {"success": False, "message": "Failed to insert vote transaction."}

    return {
        "success": True,
        "message": f"Vote recorded for proposal {proposal_id}",
        "user_id": user_id,
        "proposal_id": proposal_id,
        "tickets_used": tickets
    }


def start_new_voting_period():
    # This logic now needs to be part of the ticket purchase process,
    # and should be handled with a MongoDB update.
    # The JSON-based load_data/save_data logic is obsolete.
    pass

async def finalize_voting():
    # This entire function needs to be rewritten to use MongoDB.
    # The JSON-based load/save functions are now obsolete.
    pass

async def check_and_finalize_voting_job():
    # This function should check the MongoDB state, not a JSON file.
    # We need to access the 'is_voting_active' and 'voting_period_start_time'
    # fields from the MongoDB database, not a local file.
    pass

def record_vote_on_chain(voter_pubkey: str, proposal_id: str, tickets: int) -> dict:
    """
    Record a vote as a blockchain transaction.
    
    Args:
        voter_pubkey (str): The voter's public key (pseudonymous identity).
        proposal_id (str): The proposal the voter is voting on.
        tickets (int): The number of tickets allocated.
        
    Returns:
        dict: Transaction result with success flag and message.
    """
    # Create unique transaction ID
    tx_id = f"vote_{uuid.uuid4().hex[:10]}"
    
    # Transaction format: sender = voter, receiver = proposal_id, amount = tickets
    tx = Transactions(
        transaction_id=tx_id,
        sender=voter_pubkey,
        receiver=proposal_id,
        amount=tickets
    )
    
    # Insert into blockchain's pending transactions
    success = blockchain.insert_transaction(tx)
    if not success:
        return {"success": False, "message": "Failed to insert vote transaction."}

    # (Optional) Auto-mine a block every vote OR batch later
    block = blockchain.mine_block(data="Vote Block", miner="SYSTEM")

    # Save blockchain state
    blockchain.save_chain()

    return {
        "success": True,
        "message": f"Vote recorded: {voter_pubkey} voted {tickets} tickets on {proposal_id}",
        "tx_id": tx_id,
        "block_index": block["index"],
        "block_hash": block["hash"]
    }