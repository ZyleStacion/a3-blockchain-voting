# backend/vote.py
from fastapi import APIRouter
from feature.buy_credits import buy_voting_credits
from feature.Voting import create_vote_transaction
from db.schemas import CreditPurchaseResponse, VoteProposalCreate

vote_router = APIRouter(prefix="/vote", tags=["Vote"])

@vote_router.post("/buy-credits", response_model=CreditPurchaseResponse)
async def buy_credits_endpoint(request: CreditPurchaseResponse):
    return buy_voting_credits(request)

@vote_router.post("/submit-vote")
async def submit_vote_endpoint(request: VoteProposalCreate):
    return create_vote_transaction(request.username, request.proposal_id, request.votes)