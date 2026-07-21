import os
from pymongo import AsyncMongoClient
from beanie import init_beanie
from employees.models import Employee
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("MONGODB_URL")

async def init_db():
    global client
    client = AsyncMongoClient(url)
    await init_beanie(database=client.PunchedN, document_models=[Employee])

async def close_db():
    if client is not None:
        await client.close()