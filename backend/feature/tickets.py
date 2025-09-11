import datetime
import uuid
from db.schemas import TicketPurchase, CreditPurchaseResponse
from db.database import users_collection, get_settings_collection
from feature.Voting import start_new_voting_period # import start_new_voting_period function

async def calculate_qv_cost(tickets: int) -> int:
    """Calculates the quadratic cost of purchasing tickets."""
    return tickets ** 2

async def buy_tickets(purchase: TicketPurchase) -> CreditPurchaseResponse:
    """Handles the purchase of voting tickets using credits."""
    
    user = await users_collection.find_one({"_id": purchase.user_id})

    if not user:
        raise ValueError("Cannot find user.")

    settings_collection = get_settings_collection()
    voting_status = await settings_collection.find_one({"_id": "voting_status"})

    if voting_status.get("is_voting_active"):
        raise ValueError("You cannot purchase tickets while voting is in session.")
    
    tickets_to_buy = purchase.tickets_to_buy
    cost = await calculate_qv_cost(tickets_to_buy)

    if user.get('credit_balance', 0) < cost:
        raise ValueError("Not enough credits.")

    # 1. updates user balance and number of tickets
    await users_collection.update_one(
        {"_id": purchase.user_id},
        {"$inc": {"credit_balance": -cost, "voting_tickets": tickets_to_buy}}
    )
    
    # 2. updates donation pot and checks for vote triggers
    updated_pot_status = await settings_collection.find_one_and_update(
        {"_id": "voting_status"},
        {"$inc": {"donation_pot": cost}},
        return_document=True
    )
    
    if updated_pot_status.get("donation_pot", 0) >= updated_pot_status.get("THRESHOLD_AMOUNT", 1000) and not updated_pot_status.get("is_voting_active"):
        # call start_new_voting_period() function upon threshold reach
        await start_new_voting_period()

    # 3. return response
    updated_user = await users_collection.find_one({"_id": purchase.user_id})
    return CreditPurchaseResponse(
        user_id=updated_user["_id"],
        credits_purchased=cost
    )