from pydantic import BaseModel, Field
from typing import Dict, List, Optional

# User schemas 
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    email: str = Field(...,)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str   # <-- add this
    donation_balance: Optional[float] = 100000.0
    voting_tickets: Optional[int] = 0
    public_key: str
    
    class Config:
        form_mode = True

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
        form_mode = True
        
        
# Ticket schema
class TicketPurchase(BaseModel):
    user_id: int
    ticket_purchase: int
    
class TicketResponse(BaseModel):
    user_id: int
    ticket_purchase: int
    
    class Config:
        form_mode = True
    
# Credit purchase schema
class CreditPurchase(BaseModel):
    user_id: str
    credits_purchased: int
    
class CreditPurchaseResponse(BaseModel):
    user_id: str
    credits_purchased: int


    class Config:
        form_mode = True
        
        
# Vote proposal schema
class VoteProposalCreate(BaseModel):    
    title: str
    description: str    
    charity_id: int

class VoteProposalResponse(BaseModel):
    id: int
    title: str
    description: str
    yes_counter: int  
    
    
class VoteSubmit(BaseModel):
    user_id: int
    proposal_id: int
    tickets: int
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "proposal_id": 1,
                "tickets": 5
            }
        }


# Charity schema
class CharityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    open_time: Optional[str] = None   
    close_time: Optional[str] = None  


class CharityUpdate(BaseModel):
    open_time: Optional[str] = None
    close_time: Optional[str] = None   


class CharityResponseModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    status: Optional[str] = None

    class Config:
        orm_mode = True