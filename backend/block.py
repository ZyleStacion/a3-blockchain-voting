from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from blockchain.blockchain import Blockchain, Transactions

# ✅ Create a singleton blockchain instance
blockchain = Blockchain()

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


# Get single block by index
@router.get("/blockchain/{index}")
def get_single_block(index: int):
    if index < 0 or index >= len(blockchain.chain):
        raise HTTPException(status_code=404, detail="Block not found")
    return blockchain.chain[index]


# Mine block
@router.post("/mine_block/")
def mine_block(data: str, miner: str):
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="Invalid Blockchain")

    block = blockchain.mine_block(data=data, miner=miner)
    return {"message": f"Block mined by {miner}!", "block": block}


# --- Transactions ---

# Create transaction
@router.post("/create_transactions")
def create_transactions_form(
    id: str = Form(..., description="Transaction ID, e.g. tx001"),
    sender: str = Form(..., description="Sender name, e.g. Alice"),
    receiver: str = Form(..., description="Receiver name, e.g. Bob"),
    amount: float = Form(..., description="Amount, e.g. 100"),
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

    return {
        "accepted": True,
        "size": len(blockchain.pending_transactions),
    }


# Get pending transactions
@router.get("/pending_transactions")
def get_pending_transactions():
    return {
        "pending_transactions": blockchain.pending_transactions,
        "count": len(blockchain.pending_transactions),
    }


# Get balance of a user
@router.get("/balance/{user}")
def get_balance(user: str):
    if not user:
        raise HTTPException(status_code=400, detail="No user")

    balance = blockchain.get_balance(user)
    return {"user": user, "balance": balance}


# --- Data persistence ---

# Save chain
@router.post("/save")
def save_chain():
    try:
        blockchain.save_chain()
        return {"saved": True, "index": len(blockchain.chain)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Load chain
@router.post("/load")
def load_chain():
    try:
        blockchain.load_chain()
        return {"loaded": True, "index": len(blockchain.chain)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Blockchain file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
