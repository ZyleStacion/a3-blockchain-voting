import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test():
    client = AsyncIOMotorClient("mongodb+srv://ankhanhthinj_db_user:lhci4I2IlC4c3Qdh@donation.s0fjrkj.mongodb.net/")
    dbs = await client.list_database_names()
    print("MongoDB is running. Databases:", dbs)

asyncio.run(test())
