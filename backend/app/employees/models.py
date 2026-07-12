from beanie import Document
from pydantic import EmailStr


class Employee(Document):
    keycloak_id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
