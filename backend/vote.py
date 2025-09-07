# backend/vote.py
from fastapi import APIRouter
from feature.buy_credits import buy_voting_credits, BuyCreditsRequest
from feature.Voting import create_vote_transaction, VoteRequest

vote_router = APIRouter(prefix="/vote", tags=["vote"])

@vote_router.post("/buy-credits")
async def buy_credits(request_data: BuyCreditsRequest):
    """
    API endpoint for vote purchase
    """
    result = await buy_voting_credits(request_data.username, request_data.credits)
    return result

@vote_router.post("/submit")
async def submit_vote(request_data: VoteRequest):
    """
    API endpoint for voting
    """
    result = await create_vote_transaction(request_data.username, request_data.proposal_id, request_data.votes)
    return result
