from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
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


# Mine block
@router.post("/mine_block/")
def mine_block(data: str = "Vote Block"):
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="Invalid Blockchain")

    block = blockchain.auto_mine_block(data=data)
    if not block:
        raise HTTPException(status_code=400, detail="No pending transactions to mine")

    return {"message": "Block auto-mined!", "block": block}


# --- Transactions ---

# Create Vote transaction
@router.post("/create_transactions")
def create_transactions_form(
    id: str = Form(...),
    sender: str = Form(...),
    receiver: str = Form(...),
    amount: float = Form(...)
):
    trans = Transactions(
        transaction_id=id,
        sender=sender,
        receiver=receiver,
        amount=amount,
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

