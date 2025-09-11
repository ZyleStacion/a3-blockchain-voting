import datetime
import uuid
from db.schemas import TicketPurchase, TicketResponse
from db.save import load_data, save_data
from feature.voting import start_new_voting_period, THRESHOLD_AMOUNT

def calculate_qv_cost(tickets: int) -> int:
    """Calculates the quadratic cost of purchasing tickets."""
    return tickets ** 2

def buy_tickets(purchase: TicketPurchase) -> TicketResponse:
    """Handles the purchase of voting tickets using credits."""
    data = load_data()

    if not data:
        raise ValueError("Cannot load data file.")
    
    if data.get("is_voting_active"):
        raise ValueError("You cannot purchase tickets while voting is in session.")

    user = data['users'].get(purchase.user_id)
    if not user:
        raise ValueError("Cannot find user.")

    tickets_to_buy = purchase.tickets_to_buy
    cost = calculate_qv_cost(tickets_to_buy)

    if user['donation_balance'] < cost:
        raise ValueError("Not enough credits.")

    # Update balances
    user['donation_balance'] -= cost
    # 'voting_credits'를 'voting_tickets'로 변경하는 것이 더 명확합니다.
    user['voting_tickets'] += tickets_to_buy
    data['donation_pot'] += cost
    
    save_data(data)
    
    if data['donation_pot'] >= THRESHOLD_AMOUNT and not data.get("is_voting_active"):
        start_new_voting_period()

    # Build response
    return TicketResponse(
        user_id=purchase.user_id,
        tickets_purchased=tickets_to_buy,
    )