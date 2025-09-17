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
donation_collection = db["donations"]
charities_collection = db["charities"]
counters_collection = db["counters"]




async def get_next_user_id():
    counter = await counters_collection.find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

async def get_next_proposal_id():
    counter = await counters_collection.find_one_and_update(
        {"_id": "proposal_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

async def get_next_donation_id():
    counter = await counters_collection.find_one_and_update(
        {"_id": "donation_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

async def get_next_charity_id():
    counter = await counters_collection.find_one_and_update(
        {"_id": "charity_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]
