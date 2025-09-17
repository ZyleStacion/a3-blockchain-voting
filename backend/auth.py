from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime, timedelta
from db.database import users_collection, get_next_user_id
from db.schemas import UserCreate, UserLogin, UserResponse
from utils.DigitalSignature import generate_key

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# JWT dependency function
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        return {"user_id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def create_access_token(data: dict):
    """Create JWT token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

@router.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
 
    if db_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token(data={"user_id": db_user["user_id"]})
    
    user_data = user_helper(db_user)
    return {
        **user_data,
        "access_token": access_token,
        "token_type": "bearer"
    } 

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}

@router.get("/user-info")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        # Find user in database
        user = await users_collection.find_one({"user_id": current_user["user_id"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return user info (exclude sensitive data like password hash)
        return {
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "donation_balance": user.get("donation_balance", 0),
            "voting_tickets": user.get("voting_tickets", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user information")