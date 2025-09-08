import datetime
import uuid
from db.schemas import CreditPurchase, CreditPurchaseResponse
from db.save import load_data, save_data
from feature.Voting import start_new_voting_period, THRESHOLD_AMOUNT

def calculate_qv_cost(credits: int) -> int:
    return credits ** 2


def buy_voting_credits(purchase: CreditPurchase) -> CreditPurchaseResponse:
    data = load_data()

    if not data:
        raise ValueError("Cannot load data file.")
    
    if data.get("is_voting_active"):
        raise ValueError("You cannot purchase tickets while voting is in session.")

    user = data['users'].get(purchase.user_id)
    if not user:
        raise ValueError("Cannot find user.")

    cost = calculate_qv_cost(purchase.credits_purchased)

    if user['donation_balance'] < cost:
        raise ValueError("Not enough credits.")

    # Update balances
    user['donation_balance'] -= cost
    user['voting_credits'] += purchase.credits_purchased
    data['donation_pot'] += cost
    
    save_data(data)
    
    if data['donation_pot'] >= THRESHOLD_AMOUNT and not data.get("is_voting_active"):
        start_new_voting_period()

    # Build response
    return CreditPurchaseResponse(
        user_id=purchase.user_id,
        credits_purchased=purchase.credits_purchased,
    
    )