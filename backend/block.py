from fastapi import APIRouter,FastAPI, Form, HTTPException # type: ignore
import fastapi as _fastapi # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from pydantic import BaseModel # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

from blockchain.blockchain import Transactions
import blockchain.blockchain as block

#Set up
""" 
The setup here means that the setup can be access from any location and device
"""
router = APIRouter(prefix="/auth", tags=["Blockchain"])


# Base Model
class GetTransactions(BaseModel):
    id: str
    sender: str
    receiver: str
    amount: float

# --- End point ---
# Get all block chain
@router.get("/blockchain")
def get_blockchain_data():
    if not block.is_chain_valid():
        raise HTTPException(status_code=400, detail="Invalid Blockchain")

    return {
        "index": len(block.chain),
        "valid": True,
        "pending_count": len(getattr(block, "pending_transactions", [])),
        "pending_transactions": getattr(block, "pending_transactions", []),
        "chain": block.chain,
    }
    
# Get single block by block index
@router.get('/blockchain/{index}')
def get_blockchain_data(index: int):
    if index < 0 or index >= len(block.chain):
        raise HTTPException(status_code=404, detail="Block not found") # Validation
    return block.chain[index]


# Mine block
@router.post('/mine_block/')
def mine_block(data: str, miner: str):
    if not block.is_chain_valid():
        raise HTTPException(status_code=400, detail="Invalid Block")
    
    block = block.mine_block(data=data, miner=miner)
    return {"message": f"Block mined by {miner}!", "block": block}


#-- Transactions -- 
#Create transaction
@router.post("/create_transactions") #Ai to debug
def create_transactions_form(
    id: str = Form(..., description="Transaction ID, e.g. tx001"),
    sender: str = Form(..., description="Sender name, e.g. Alice"),
    receiver: str = Form(..., description="Receiver name, e.g. Bob"),
    amount: float = Form(..., description="Amount, e.g. 100"),):
    trans = Transactions(
        transaction_id=id,
        sender=sender,
        receiver=receiver,
        amount=amount,
    )

    valid = block.insert_transaction(trans)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid Transaction")

    return {
        "accepted": True,
        "size": len(getattr(block, "pending_transactions", [])),   
    }

# Get pending transactions
@router.get("/pending_transactions")
def get_pending_transactions():
     return {
        "pending_transactions": getattr(block, "pending_transactions", []),
        "count": len(getattr(block, "pending_transactions", [])),
    }

# Get balance of user
@router.get("/balance/{user}")
def get_balance(user: str):
    if not user:
        raise HTTPException(status_code=400, detail="No user")
    
    balance = block.get_balance(user)
    return {"user": user, "balance": balance}



# Data persistence
# Save block, whenevevr new block or transactions is added
@router.post("/save")
def save_chain():
    try:
        block.save_chain()
        return {"saved": True, "index": len(block.chain)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Load Json file
@router.post("/load")
def load_chain():
    try:
        block.load_chain()
        return {"loaded": True, "index": len(block.chain)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Blockchain file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

