# backend/vote.py
from fastapi import APIRouter
from feature.buy_credits import buy_voting_credits
from feature.Voting import create_vote_transaction
from db.schemas import CreditPurchaseResponse, VoteProposalCreate, VoteSubmit

vote_router = APIRouter(prefix="/vote", tags=["Vote"])

@vote_router.post("/buy-credits", response_model=CreditPurchaseResponse)
def buy_credits_endpoint(request: CreditPurchaseResponse):
    return buy_voting_credits(request)

@vote_router.post("/create-proposal")
def create_proposal_endpoint(request: VoteProposalCreate):
    # store proposal in DB or chain
    return {"success": True, "message": f"Proposal '{request.title}' created."}

@vote_router.post("/submit-vote")
def submit_vote_endpoint(request: VoteSubmit):
    return create_vote_transaction(
        request.user_id,      
        request.proposal_id,
        request.votes
    )