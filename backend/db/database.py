import json
import os
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAIN_FILE_PATH = os.path.join(BASE_DIR, 'chain.json')
DATA_FILE_PATH = os.path.join(BASE_DIR, 'data.json')

def load_chain_data() -> List[Dict[str, Any]]:
    if not os.path.exists(CHAIN_FILE_PATH):
        return []
    try:
        with open(CHAIN_FILE_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_chain_data(chain: List[Dict[str, Any]]):
    with open(CHAIN_FILE_PATH, 'w') as f:
        json.dump(chain, f, indent=4)

def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE_PATH):
        initial_data = {
            "users": {
                "user_A": {"donation_balance": 1000, "voting_credits": 0},
                "user_B": {"donation_balance": 500, "voting_credits": 0}
            },
            "proposals": {
                "proposal_1": {"name": "child support", "description": "Help children in need."},
                "proposal_2": {"name": "Environment protection", "description": "Facilitate the environment for future generation."}
            },
            "donation_pot": 0,
            "current_transactions": [],
            "is_voting_active": False,
            "voting_period_start_time": None
        }
        with open(DATA_FILE_PATH, 'w') as f:
            json.dump(initial_data, f, indent=4)
        return initial_data
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def save_data(data: Dict[str, Any]):
    with open(DATA_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)