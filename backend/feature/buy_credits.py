from pydantic import BaseModel
from typing import Dict, Any
from db.save import load_data, save_data
from feature.Voting import start_new_voting_period, THRESHOLD_AMOUNT

class BuyCreditsRequest(BaseModel):
    username: str
    credits: int

def calculate_qv_cost(credits: int) -> int:
    return credits ** 2

async def buy_voting_credits(username: str, credits_to_buy: int) -> Dict[str, Any]:
    data = load_data()

    if not data:
        return {"success": False, "message": "Cannot load data file."}
    
    if data.get("is_voting_active"):
        return {"success": False, "message": "You cannot purchase tickets while voting is in session."}

    user = data['users'].get(username)
    if not user:
        return {"success": False, "message": "Cannot find user."}

    cost = calculate_qv_cost(credits_to_buy)

    if user['donation_balance'] < cost:
        return {"success": False, "message": "Not enough credits."}

    user['donation_balance'] -= cost
    user['voting_credits'] += credits_to_buy
    data['donation_pot'] += cost
    
    save_data(data)
    
    if data['donation_pot'] >= THRESHOLD_AMOUNT and not data.get("is_voting_active"):
        start_new_voting_period()

    return {"success": True, "message": f"'{username}'has purchased {credits_to_buy} tickets with {cost} $.", "new_balance": user['voting_credits']}