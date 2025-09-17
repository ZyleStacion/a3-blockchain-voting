# backend/main.py
from fastapi import FastAPI, APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.save import load_data
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from vote import vote_router as vote_router
from block import router as block_router
from donation import donation_router as donation_router
from blockchain.blockchain_singleton import blockchain
from charity import charity_router as charity_router
import uvicorn

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    blockchain.load_chain()
    print("Blockchain loaded from file.")
except FileNotFoundError:
    print("No existing blockchain file. Starting fresh.")
    
@router.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}

# Include routers
app.include_router(auth_router)
app.include_router(vote_router)
app.include_router(donation_router)
app.include_router(block_router)
app.include_router(charity_router)

if __name__ == "__main__": # Alow to be access from anywhere
    uvicorn.run(app, host="0.0.0.0", port=8000)