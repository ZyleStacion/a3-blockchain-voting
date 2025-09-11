# backend/main.py
from fastapi import FastAPI, APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.save import load_data
from feature.voting import check_and_finalize_voting_job
from vote import vote_router  
from auth import router as auth_router
<<<<<<< HEAD
from block  import router as block_router
=======
from fastapi.middleware.cors import CORSMiddleware
from vote import vote_router as vote_router
>>>>>>> 129b2b1934790111e0089b976bd1dca1d34fed28


# Set up
app = FastAPI()
router = APIRouter()
app.include_router(router)

# Add CORS middleware - allows web browser to accept requests from different origins
# Allow frontend (Vite) + any others you need
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # sometimes Vite uses 127.0.0.1
]

<<<<<<< HEAD
# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.start()


# Schedules the job to check for voting finalization every minute
scheduler.add_job(check_and_finalize_voting_job, 'interval', seconds=60)
=======
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@router.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}
>>>>>>> 129b2b1934790111e0089b976bd1dca1d34fed28

# Include routers
app.include_router(auth_router)
app.include_router(vote_router)
app.include_router(block_router)

# Status endpoint
@app.get("/api/status")
async def get_status():
    data = load_data()
    return data