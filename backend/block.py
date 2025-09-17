from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel
from blockchain.blockchain import Transactions
from blockchain.blockchain_singleton import blockchain  

# Router setup
router = APIRouter(prefix="/blockchain", tags=["Blockchain"])

# --- Models ---
class GetTransactions(BaseModel):
    id: str
    sender: str
    receiver: str
    amount: float


# --- Endpoints ---

# Get all blockchain data
@router.get("/blockchain")
def get_blockchain_data():
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="Invalid Blockchain")

    return {
        "index": len(blockchain.chain),
        "valid": True,
        "pending_count": len(blockchain.pending_transactions),
        "pending_transactions": blockchain.pending_transactions,
        "chain": blockchain.chain,
    }


# --- Transactions ---

# Create Vote transaction
@router.post("/create_vote_transaction")
def create_vote_transaction(
    id: str = Form(...),
    sender: str = Form(...),
    charity_receive: str = Form(...),
    ticket_sent: int = Form(...)
):
    trans = Transactions(
        transaction_id=id,
        sender=sender,
        charity_receive=charity_receive,
        ticket_sent=ticket_sent,
    )

    valid = blockchain.insert_transaction(trans)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid Transaction")

    # Auto-mine right after transaction is added
    block = blockchain.auto_mine_block(data="Vote Block")

    return {
        "accepted": True,
        "block_mined": bool(block),
        "block": block,
        "chain_length": len(blockchain.chain),
    }

