from fastapi import FastAPI, APIRouter
from auth import router as auth_router
from vote import vote_router as vote_router


# Set up
app = FastAPI()
router = APIRouter()
app.include_router(router)


@router.get("/")
def test_endpoint():
    return {"message": "Welcome to the Blockchain Voting API"}

# Include routers
app.include_router(router)
app.include_router(auth_router)
app.include_router(vote_router)