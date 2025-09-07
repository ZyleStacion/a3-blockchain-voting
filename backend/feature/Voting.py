from pydantic import BaseModel
from typing import Dict, Any, List
from ..db.database import load_data, save_data, load_chain_data, save_chain_data
import json
import time
import hashlib

THRESHOLD_AMOUNT = 1000
VOTING_PERIOD_SECONDS = 300

class VoteRequest(BaseModel):
    username: str
    proposal_id: str
    votes: int

def calculate_hash(data_dict: Dict[str, Any]) -> str:
    block_string = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

async def create_vote_transaction(username: str, proposal_id: str, votes: int) -> Dict[str, Any]:
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
        
    user['voting_credits'] -= votes
    
    transaction = {
        "voter": username,
        "proposal_id": proposal_id,
        "votes": votes,
        "timestamp": time.time()
    }
    
    data['current_transactions'].append(transaction)
    save_data(data)

    return {"success": True, "message": f"'{username}' has voted {votes} tickets to '{proposal_id}'."}

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