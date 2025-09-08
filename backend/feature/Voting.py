from typing import Dict, Any, List
import uuid
from db.save import load_data, save_data, load_chain_data, save_chain_data
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

def create_vote_transaction(username: str, proposal_id: str, votes: int) -> Dict[str, Any]:
    data = load_data()
    if not data:
        return {"success": False, "message": "Cannot load data file."}
    
    if not data.get("is_voting_active"):
        return {"success": False, "message": "Not in voting session."}

    user = data['users'].get(username)
    if not user:
        return {"success": False, "message": "User cannot be found."}

    if user['voting_credits'] < votes:
        return {"success": False, "message": "Not enough tickets."}
        
    # Deduct credits
    user['voting_credits'] -= votes
    save_data(data)

    # Create unique transaction ID
    tx_id = f"vote_{uuid.uuid4().hex[:10]}"

    # Use public key as pseudonymous identity
    voter_pubkey = user.get("wallet_address", username)

    # Build blockchain transaction
    tx = Transactions(
        transaction_id=tx_id,
        sender=voter_pubkey,      # voter’s public key
        receiver=proposal_id,     # proposal being voted on
        amount=votes              # number of votes
    )

    # Insert into blockchain pending txs
    success = blockchain.insert_transaction(tx)
    if not success:
        return {"success": False, "message": "Failed to insert vote transaction."}

    # Mine the block immediately (optional: could batch instead)
    block = blockchain.mine_block(data="Vote Block", miner="SYSTEM")

    # Save blockchain state
    blockchain.save_chain()

    return {
        "success": True,
        "message": f"Vote recorded on-chain: {voter_pubkey} voted {votes} on proposal {proposal_id}",
        "tx_id": tx_id,
        "block_index": block["index"],
        "block_hash": block["hash"]
    }

def start_new_voting_period():
    data = load_data()
    if data and not data.get("is_voting_active"):
        data["is_voting_active"] = True
        data["voting_period_start_time"] = time.time()
        save_data(data)
        print("Pot has reached overflow threshold. Initiating vote.")

async def finalize_voting():
    data = load_data()
    chain = load_chain_data()

    prev_hash = "0"
    if chain:
        last_block = chain[-1]
        prev_hash = last_block['hash']
    
    new_block = {
        "index": len(chain),
        "timestamp": time.time(),
        "transactions": data['current_transactions'],
        "prev_hash": prev_hash
    }
    new_block['hash'] = calculate_hash(new_block)
    
    chain.append(new_block)
    save_chain_data(chain)

    vote_counts = {}
    for tx in data['current_transactions']:
        prop_id = tx['proposal_id']
        vote_counts[prop_id] = vote_counts.get(prop_id, 0) + tx['votes']
    
    if vote_counts:
        winner = max(vote_counts, key=vote_counts.get)
        donation_amount = data['donation_pot']
        
        print(f"\n[Result] The winner of the vote is '{winner}'. A total of {donation_amount}$ will be donated.")
        
        data['donation_pot'] = 0
    
    data['current_transactions'] = []
    data['is_voting_active'] = False
    data['voting_period_start_time'] = None
    save_data(data)
    print("Votes were concluded and blocks were created.")

async def check_and_finalize_voting_job():
    data = load_data()
    if data and data.get("is_voting_active") and data.get("voting_period_start_time"):
        elapsed_time = time.time() - data.get("voting_period_start_time")
        if elapsed_time >= VOTING_PERIOD_SECONDS:
            await finalize_voting()
            

def record_vote_on_chain(voter_pubkey: str, proposal_id: str, votes: int) -> dict:
    """
    Record a vote as a blockchain transaction.

    Args:
        voter_pubkey (str): The voter's public key (pseudonymous identity).
        proposal_id (str): The proposal the voter is voting on.
        votes (int): The number of votes allocated.

    Returns:
        dict: Transaction result with success flag and message.
    """
    # Create unique transaction ID
    tx_id = f"vote_{uuid.uuid4().hex[:10]}"
    
    # Transaction format: sender = voter, receiver = proposal_id, amount = votes
    tx = Transactions(
        transaction_id=tx_id,
        sender=voter_pubkey,
        receiver=proposal_id,
        amount=votes
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
        "message": f"Vote recorded: {voter_pubkey} voted {votes} on {proposal_id}",
        "tx_id": tx_id,
        "block_index": block["index"],
        "block_hash": block["hash"]
    }