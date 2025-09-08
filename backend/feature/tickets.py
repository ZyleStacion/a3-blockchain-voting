import datetime
import uuid
from db.schemas import TicketPurchase, TicketResponse
from db.save import load_data, save_data
from feature.voting import start_new_voting_period, THRESHOLD_AMOUNT

def calculate_qv_cost(credits: int) -> int:
    return credits ** 2


def buy_tickets(purchase: TicketPurchase) -> TicketResponse:
    data = load_data()

    if not data:
        raise ValueError("Cannot load data file.")
    
    if data.get("is_voting_active"):
        raise ValueError("You cannot purchase tickets while voting is in session.")

    user = data['users'].get(purchase.user_id)
    if not user:
        raise ValueError("Cannot find user.")

    cost = calculate_qv_cost(purchase.ticket_purchase)

    if user['donation_balance'] < cost:
        raise ValueError("Not enough credits.")

    # Update balances
    user['donation_balance'] -= cost
    user['voting_credits'] += purchase.ticket_purchase
    data['donation_pot'] += cost
    
    save_data(data)
    
    if data['donation_pot'] >= THRESHOLD_AMOUNT and not data.get("is_voting_active"):
        start_new_voting_period()

    # Build response
    return TicketPurchase(
        user_id=purchase.user_id,
        credits_purchased=purchase.ticket_purchase,
    
    )