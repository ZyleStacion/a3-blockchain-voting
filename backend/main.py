from fastapi import FastAPI, APIRouter
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from vote import vote_router as vote_router


# Set up
app = FastAPI()
router = APIRouter()
app.include_router(router)

# Add CORS middleware - allows web browser to accept requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}

# Include routers
app.include_router(router)
app.include_router(auth_router)
app.include_router(vote_router)