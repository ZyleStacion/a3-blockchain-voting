from pydantic import BaseModel, Field
from typing import Optional

# User schemas 
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    email: str = Field(...,)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str   # <-- add this
    public_key: str
    
    class Config:
        orm_mode = True

# Vote schema
class VoteCreate(BaseModel):
    proposal_id: str
    choice: str  # e.g. "yes", "no", "abstain"

class VoteResponse(BaseModel):
    id: str
    user_id: str
    proposal_id: str
    choice: str
    signature: Optional[str] = None
    
# Transaction schema
class TransactionCreate(BaseModel):
    from_address: str
    to_address: str
    amount: float
    
class TransactionResponse(BaseModel):
    id: str
    from_address: str
    to_address: str
    amount: float
    timestamp: str  # ISO format
    
    class Config:
        orm_mode = True
        
        
#Ticket schema
class TicketCreate(BaseModel):
    user_id: str
    voting_credits: int
    donation_balance: float
    
class TicketResponse(BaseModel):
    id: str
    user_id: str
    voting_credits: int
    donation_balance: float
    
    class Config:
        orm_mode = True
    
# Credit purchase schema
class CreditPurchase(BaseModel):
    user_id: str
    credits_purchased: int
    
class CreditPurchaseResponse(BaseModel):
    user_id: str
    credits_purchased: int

    
    class Config:
        orm_mode = True
        
        
# Vote proposal schema
class VoteProposalCreate(BaseModel):    
    title: str
    description: str    
    options: list[str]  # e.g. ["yes", "no", "abstain"]

    
class VoteProposalResponse(BaseModel):
    id: str
    title: str
    description: str
    options: list[str]

class VoteSubmit(BaseModel):
    user_id: str         
    proposal_id: str
    votes: int
    
    class Config:
        orm_mode = True