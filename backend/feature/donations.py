# Donations
from time import time
from fastapi import HTTPException 
import uuid
from db.schemas import DonationCreate, DonationResponse
from blockchain.blockchain import Transactions
from blockchain.blockchain_singleton import blockchain 


def process_donations(input: DonationCreate) -> DonationResponse: 
  # 1. Create transaction object
    tx = Transactions(
        transaction_id=str(uuid.uuid4()),       # unique tx ID
        sender=input.user_id,
        receiver="DAO_POOL",                    # donation sink address
        amount=input.amount
    )

    # 2. Insert into pending transaction pool
    inserted = blockchain.insert_transaction(tx)
    if not inserted:
        raise HTTPException(400, detail="Invalid or duplicate transaction")

    # 3. Optionally: auto-mine the block here, or let someone else mine it later
    blockchain.mine_block(data="donation", miner="SYSTEM")

    # 4. Save updated chain
    blockchain.save_chain()

    # 5. Return response
    return DonationResponse(
        id=tx.ids,
        user_id=input.user_id,
        amount=input.amount,

    )