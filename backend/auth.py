from fastapi import APIRouter, HTTPException
from db.database import users_collection, get_next_user_id
from db.schemas import UserCreate, UserLogin, UserResponse
from utils.DigitalSignature import generate_key

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Utility: Convert Mongo doc to dict
def user_helper(user) -> dict:
    return {
        "id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "public_key": user.get("public_key", None)
    }

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    private_key, public_key = generate_key()

    user_id = await get_next_user_id()

    user_doc = {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,      
        "public_key": public_key,
        "donation_balance": 0.0,        
        "voting_tickets": 0             
    }


    result = await users_collection.insert_one(user_doc)
    new_user = await users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
 
    if db_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user_helper(db_user) 

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
