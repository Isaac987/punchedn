import os
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

load_dotenv()

url = os.getenv("MONGODB_URL")

client = AsyncMongoClient(url, serverSelectionTimeoutMS=5000)

# Testing the Connection to the MongoDB Atlas Cluster

async def test_connection():
    try:
        result = await client.admin.command("ping")
        print("Successful Connection to MongoDB Atlas")
        print(result)
    except PyMongoError:
        print("Connction Failed: PyMongoError")

# Testing the connection to the Database

async def test_db_connection():
    try:
        collection = client.PunchedN.Employees
        print("Successfully Connected to Employee Database")
        count = await collection.count_documents({})
        print("Number of Employee Documents", count)
    except PyMongoError:
        print("Employee Database Connection Failed: PyMongoError")

# Closing the connection to the Database

async def close_connection():
    await client.close()