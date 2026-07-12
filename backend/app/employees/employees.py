import os
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv()
url = os.getenv("MONGODB_URL")
client = AsyncMongoClient(url)
collection = client.PunchedN.Employees

# CRUD

# Create one Employee
async def create_employee(employee_data):
    result = await collection.insert_one(employee_data)
    return print(f"Employee Added Successfully, ID: {result.inserted_id} Status: {result.acknowledged}")

# Create multiple Employees
async def create_employees(employee_data):
    result = await collection.insert_many(employee_data)
    return print(f"Employees Added Successfully, ID: {result.inserted_id} Status: {result.acknowledged}")

# Read one Employee
async def read_one_employee(employee_id):
    result = await collection.find_one({"_id": employee_id})
    return print(result)

# Read all the Employees
async def read_all_employees():
    cursor = collection.find()
    async for employee in cursor:
        print(employee)

# Update one Employee's Details
async def update_one_employee(employee_id, updated_data):
    result = await collection.update_one({"_id": employee_id}, {"$set": updated_data})
    return print(f"Employee Data Successfully Updated, ID: {employee_id} Status: {result.acknowledged}")

# Update many Employee's Details
async def update_many_employees(field, criteria, updated_data):
    result = await collection.update_many({field: criteria}, {"$set": updated_data})
    return print(f"Employees with {field} = {criteria} has been Successfully Updated, Status: {result.acknowledged}")

# Delete one Employee
async def delete_one_employee(employee_id):
    await collection.delete_one({"_id": employee_id})
    print(f"Employee with ID: {employee_id} Successfully Deleted")

# Delete Many Employees
async def delete_many_employees(field, criteria):
    await collection.delete_many({field: criteria})
    return print(f"Employees with {field} = {criteria} has been Successfully Deleted.")