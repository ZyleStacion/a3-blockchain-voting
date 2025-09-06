# backend/main.py
from fastapi import FastAPI, APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from .feature.buy_credits import buy_voting_credits, BuyCreditsRequest
from feature.Voting import check_and_finalize_voting_job
from vote import vote_router
from db.database import load_data, save_data

# Set up
app = FastAPI()
router = APIRouter()
app.include_router(router)

# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.start()
 
# Schedule the job to check for voting finalization every minute
scheduler.add_job(check_and_finalize_voting_job, 'interval', seconds=60)

@router.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}

# Include routers
app.include_router(router)
#app.include_router(auth_router)
app.include_router(vote_router)

# Status endpoint
@app.get("/api/status")
async def get_status():
    data = load_data()
    return data