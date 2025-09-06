# backend/main.py

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .vote import vote_router  # <-- Corrected import path
from .db.database import load_data

# Set up
app = FastAPI()

# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.start()

# Moved the check_and_finalize_voting_job to its own function in Voting.py
from .feature.Voting import check_and_finalize_voting_job

# Schedules the job to check for voting finalization every minute
scheduler.add_job(check_and_finalize_voting_job, 'interval', seconds=60)

# Include routers
#app.include_router(router)
#app.include_router(auth)
app.include_router(vote_router)

# Status endpoint
@app.get("/api/status")
async def get_status():
    data = load_data()
    return data