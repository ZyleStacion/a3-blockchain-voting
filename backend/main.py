from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .feature.Voting import check_and_finalize_voting_job
from .auth import router as auth_router
from .vote import vote_router
from .block import router as block_router
from .db.database import get_settings_collection

# Set up FastAPI app
app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up APScheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(check_and_finalize_voting_job, IntervalTrigger(seconds=10)) # checks for vote end every 10 seconds.
scheduler.start()

# Include routers
app.include_router(auth_router)
app.include_router(vote_router)
app.include_router(block_router)

# Status endpoint to check the voting status from MongoDB
@app.get("/api/status")
async def get_status():
    settings_collection = get_settings_collection()
    voting_status = await settings_collection.find_one({"_id": "voting_status"})
    return {"status": "ok", "voting_status": voting_status}

@app.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}