# backend/main.py
from fastapi import FastAPI, APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.save import load_data
from feature.voting import check_and_finalize_voting_job
from vote import vote_router  # <-- Corrected import path
from auth import router as auth_router
from block  import router as block_router


# Set up
app = FastAPI()
router = APIRouter()
app.include_router(router)


# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.start()


# Schedules the job to check for voting finalization every minute
scheduler.add_job(check_and_finalize_voting_job, 'interval', seconds=60)

# Include routers
app.include_router(auth_router)
app.include_router(vote_router)
app.include_router(block_router)

# Status endpoint
@app.get("/api/status")
async def get_status():
    data = load_data()
    return data