from typing import Dict, Any, List
import uuid
from db.database import proposals_collection, users_collection
from blockchain.blockchain import Blockchain, Transactions
from blockchain.blockchain_singleton import blockchain
import json
import time
import hashlib

THRESHOLD_AMOUNT = 1000
VOTING_PERIOD_SECONDS = 300


def calculate_hash(data_dict: Dict[str, Any]) -> str:
    block_string = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


async def create_vote_transaction(user_id: int, proposal_id: int, tickets: int):
    # 1) Verify user & tickets
    user = await users_collection.find_one({"user_id": int(user_id)})
    if not user:
        return {"success": False, "message": f"User ID {user_id} not found."}

    if user.get("voting_tickets", 0) < tickets:
        return {"success": False, "message": "Not enough voting tickets."}

    # 2) Verify proposal
    proposal = await proposals_collection.find_one({"proposal_id": int(proposal_id)})
    if not proposal:
        return {"success": False, "message": f"Proposal ID {proposal_id} not found."}

    tx_id = f"vote_{user_id}_{proposal_id}_{tickets}"

    vote_tx = Transactions(
        transaction_id=tx_id,
        sender=int(user_id),
        charity_receive=int(proposal_id),
        ticket_sent=tickets
    )

    # 4) Insert vote into blockchain pending pool
    valid = blockchain.insert_transaction(vote_tx)
    if not valid:
        return {"success": False, "message": "Failed to insert vote transaction (duplicate or invalid)."}

    # 5) Auto-mine a block that includes this vote
    block = blockchain.auto_mine_block(data="Vote Block")
    if not block:
        # rollback pending tx if mining failed
        blockchain.pending_transactions = [
            tx for tx in blockchain.pending_transactions if tx.get("id") != tx_id
        ]
        return {"success": False, "message": "Failed to mine vote block."}

    # 6) Deduct tickets ONLY AFTER block is successfully mined
    await users_collection.update_one(
        {"user_id": int(user_id)},
        {"$inc": {"voting_tickets": -tickets}}
    )

    # 7) Increment YES counter in proposal
    await proposals_collection.update_one(
        {"proposal_id": int(proposal_id)},
        {"$inc": {"yes_counter": tickets}}   # ✅ increment yes votes by number of tickets
    )

    # (optional) Persist chain so you can see it after restart
    blockchain.save_chain()

    return {
        "success": True,
        "message": f"Vote recorded for proposal {proposal_id}",
        "block_index": block["index"],
        "block_hash": block["hash"],
        "transactions": block["transactions"]
    }



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
    
    # 1. Get all pending transactions from the blockchain
    current_transactions = blockchain.pending_transactions
    if not current_transactions:
        print("No transactions to finalize.")
        
    # 2. Count votes and store the first vote timestamp for each proposal
    vote_counts = {}
    first_vote_timestamps = {}
    for tx in current_transactions:
        prop_id = tx.receiver
        tickets_cast = tx.amount
        
        # Count total tickets per proposal
        vote_counts[prop_id] = vote_counts.get(prop_id, 0) + tickets_cast
        
        # Record the timestamp of the first vote if it doesn't exist
        if prop_id not in first_vote_timestamps:
            first_vote_timestamps[prop_id] = tx.timestamp # Assuming Transactions has a timestamp
    
    # 3. Handle the vote results
    if vote_counts:
        # Get the maximum number of tickets
        max_tickets = max(vote_counts.values())
        
        # Find all proposals that are tied with the max number of tickets
        tied_proposals = [
            prop_id for prop_id, count in vote_counts.items() 
            if count == max_tickets
        ]
        
        # 4. Determine the winner based on the tie-breaker rule
        if len(tied_proposals) == 1:
            # No tie, simply pick the single winner
            winner_id = tied_proposals[0]
        else:
            # A tie exists, use the first-in rule
            # Find the winner among tied proposals based on the earliest timestamp
            winner_id = min(tied_proposals, key=lambda prop: first_vote_timestamps[prop])
            
        settings_collection = get_settings_collection()
        voting_status = await settings_collection.find_one({"_id": "voting_status"})
        donation_amount = voting_status.get("donation_pot", 0)

        # 5. Announce results and reset donation pot
        print(f"\n[Result] The winner of the vote is '{winner_id}'. A total of {donation_amount}$ will be donated.")
        
        await settings_collection.update_one(
            {"_id": "voting_status"},
            {"$set": {"donation_pot": 0}}
        )
    
    # 6. Finalize the blockchain and reset voting status
    new_block = blockchain.mine_block(data="Final Vote Block", miner="SYSTEM")
    blockchain.save_chain()
    
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