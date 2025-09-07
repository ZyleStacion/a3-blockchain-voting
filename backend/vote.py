# backend/vote.py

from fastapi import APIRouter
from feature.buy_credits import buy_voting_credits, BuyCreditsRequest
from feature.Voting import create_vote_transaction, VoteRequest

vote_router = APIRouter(prefix="/vote", tags=["vote"])

@vote_router.post("/buy-credits")
async def buy_credits_endpoint(request: BuyCreditsRequest):
    return await buy_voting_credits(request.username, request.credits)

@vote_router.post("/submit-vote")
async def submit_vote_endpoint(request: VoteRequest):
    return await create_vote_transaction(request.username, request.proposal_id, request.votes)