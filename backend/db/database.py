from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://ankhanhthinj_db_user:lhci4I2IlC4c3Qdh@donation.s0fjrkj.mongodb.net/"  # or your MongoDB Atlas URI
DB_NAME = "donation_dao"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
votes_collection = db["votes"]
transactions_collection = db["transactions"]
proposals_collection = db["proposals"]