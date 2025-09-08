# backend/vote.py
from fastapi import APIRouter
from feature.tickets import buy_tickets
from feature.voting import create_vote_transaction, start_new_voting_period
from db.schemas import CreditPurchaseResponse, VoteProposalCreate, VoteSubmit

vote_router = APIRouter(prefix="/vote", tags=["Vote"])
start_new_voting_period()

@vote_router.post("/buy-tickets", response_model=CreditPurchaseResponse)
def buy_credits_endpoint(request: CreditPurchaseResponse):
    return buy_tickets(request)

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