from fastapi import HTTPException
from db.schemas import TicketPurchase
from db.database import users_collection


def calculate_qv_cost(tickets: int) -> int:
    """Calculates the quadratic cost of purchasing tickets."""
    return tickets ** 2

async def buy_tickets(purchase: TicketPurchase) -> dict:
    """
    Handles the purchase of voting tickets using credits.
    Validation flow is similar to create_vote_transaction.
    """

    # 1. Verify user exists
    user = await users_collection.find_one({"user_id": purchase.user_id})
    if not user:
        return {"success": False, "message": f"User ID {purchase.user_id} not found."}

    ticket_purchase = purchase.ticket_purchase
    cost = calculate_qv_cost(ticket_purchase)

    # 2. Verify user has enough credits
    donation_balance = user.get("donation_balance", 0)
    if donation_balance < cost:
        return {"success": False, "message": "Not enough credits."}

    # 3. Update balances atomically
    await users_collection.update_one(
        {"user_id": purchase.user_id},
        {
            "$inc": {
                "donation_balance": -cost,
                "voting_tickets": ticket_purchase
            }
        }
    )

    # 4. Return response (consistent with your transaction pattern)
    return {
        "success": True,
        "message": f"Purchased {ticket_purchase} tickets.",
        "user_id": purchase.user_id,
        "tickets_purchased": ticket_purchase,
        "remaining_balance": donation_balance - cost,  # Include updated balance in response
        "total_tickets": user.get("voting_tickets", 0) + ticket_purchase
    }

